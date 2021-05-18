import os
import re
import subprocess
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Sequence,
    Type,
    TypedDict,
    TypeVar,
)

from app.database import BaseModel, ExtendedModel, db
from flask_migrate import revision

T = TypeVar("T")

X = TypeVar("X")


def chain(*functions: Callable[[T], T]) -> Callable[[T], T]:
    """Create a chained function

    Returns:
        Callable[[T], T]: Iterable of callables that accept the same arguments
    """

    def returned_function(var: T) -> T:
        for func in functions:
            var = func(var)
        return var

    return returned_function


def argument_list_type(type_: Type[X]):
    """Custom function to cast request parser list argments

    Args:
        type_ (T): Basic type to try and cast list elements
    """

    def checker(val: Any) -> List[X]:
        assert isinstance(val, list)
        if not isinstance(val, list) and False in [
            isinstance(val_, type_) for val_ in val
        ]:
            raise TypeError
        return [type_(val_) for val_ in val]  # type: ignore

    return checker


class ColumnData(TypedDict):
    name: str
    type: str
    comment: str


class TypedTableData(TypedDict):
    type: Literal["view", "table"]
    model: Dict[Literal["name", "path"], str]
    description: str
    columns: List[ColumnData]


def get_tables_data() -> Dict[str, TypedTableData]:
    def module_path(attrs):
        return os.path.join(*(attrs[:-1] + [attrs[-1] + ".py"]))

    models: Sequence[Type[ExtendedModel]] = BaseModel.__subclasses__()

    result: Dict[str, TypedTableData] = {}
    for table in sorted(
        models,
        key=lambda model: model.__name__,
    ):
        result[table.__tablename__] = {
            "type": "view" if getattr(table, "is_view", False) else "table",
            "model": {
                "name": table.__name__,
                "path": module_path(table.__module__.split(".")),
            },
            "description": table.__doc__,
            "columns": [
                {
                    "name": col.name,
                    "type": str(col.type),
                    "comment": col.comment,
                    "primary/foreign": "primary"
                    if col.primary_key
                    else "foreign"
                    if len((col.foreign_keys or [])) > 0
                    else "n/a",
                }
                for col in table.__table__.columns
            ],
            "constraints": [
                {
                    "name": constrain.name,
                    "type": constrain.__class__.__name__,
                    "columns": [col.name for col in constrain.columns],  # type: ignore
                }
                for constrain in sorted(
                    table.__table__.constraints,
                    key=lambda constrain: constrain.__class__.__name__,
                )
            ],
        }
    if getattr(table, "is_view", False):
        result[table.__tablename__]["ddl"] = table.get_ddl()  # type: ignore

    return result


def get_version_info():
    proc = subprocess.Popen(["flask", "db", "show"], stdout=subprocess.PIPE)
    out = proc.communicate()[0]
    regx = re.compile(
        r"Rev:\s(?P<revision>[0-9a-z]*)\s.*\sParent:[\s.]*(?P<parent>[0-9a-z]*)[\s.]*\sPath: (?P<path>.*\.py)\s.*"
    )

    version_info = regx.match(str(out.decode()).replace("\n", " ")).groupdict()
    return version_info


def generate_op(changed_views: List[Dict[Literal["new_ddl", "old_ddl"], str]]) -> None:
    # if len(changed_views) == 0:
    #     return
    version_info = get_version_info()
    current_db_version = db.session.execute(
        "SELECT version_num FROM alembic_version limit(1);"
    ).scalar()
    if current_db_version == version_info["revision"] and len(changed_views) > 0:
        revision("migrations")
    version_info = get_version_info()
    downgrade_pattern = (
        "(?P<downgrade>def downgrade.*((# ### end Alembic commands ###)|(pass)))"
    )
    upgrade_pattern = f"(?P<upgrade>def upgrade.*((# ### end Alembic commands ###)|(pass)))(?P<downgrade_wrapper>.*{downgrade_pattern})"
    regx_version_edit = re.compile(fr"(?P<start>.*){upgrade_pattern}\s*", re.S)

    with open(version_info["path"], "r") as fp:
        rev_text = fp.read()
    try:
        matched = regx_version_edit.match(rev_text)
        assert matched is not None
        generated_op = {
            "upgrade": (
                matched.group("upgrade").replace("\npass", "")
                + "\n\t"
                + "{}".format(
                    "\n\t".join(
                        [
                            'op.execute(\n\t\t"""\n\t\t{}\n\t"""\n\t)'.format(
                                view["new_ddl"]
                            )
                            for view in changed_views
                        ]
                    )
                )
            ),
            "downgrade": (
                matched.group("downgrade").replace(r"\npass", "\n")
                + "\n\t"
                + "{}".format(
                    "\n\t".join(
                        [
                            'op.execute(\n\t\t"""\n\t\t{}\n\t"""\n\t)'.format(
                                view["old_ddl"]
                            )
                            for view in changed_views
                        ]
                    )
                )
            ),
        }

        with open(version_info["path"], "w") as fp:
            fp.write(
                re.compile(downgrade_pattern, re.S)
                .sub(
                    generated_op["downgrade"],
                    re.compile(upgrade_pattern, re.S).sub(
                        fr"{generated_op['upgrade']}\g<downgrade_wrapper>", rev_text
                    ),
                )
                .expandtabs(4)
            )
    except AssertionError:
        print("Error matching revision to pattern")
