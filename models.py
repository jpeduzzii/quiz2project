from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
# https://en.wikipedia.org/wiki/List_of_Star_Wars_Legends_characters
class Bio(SQLModel, table=True):
    first_name: str = Field(primary_key=True)
    last_name: str = Field(primary_key=True)
    series: str = Field(primary_key=True)
    team: str
    dob: str
    position: str


class Stats(SQLModel, table=True):
    # use composite primary key (first_name, last_name) and link to Bio
    first_name: str = Field(foreign_key="bio.first_name", primary_key=True)
    last_name: str = Field(foreign_key="bio.last_name", primary_key=True)
    gp: int
    goals: int
    assists: int
    points: int
    pim: int

engine = create_engine("sqlite:///hockey.db")
SQLModel.metadata.create_all(engine)


def load_characters_before_games(html_path: str, series_value: str = "unknown"):
    """Parse the provided HTML file, extract character names appearing before the
    "Databank | Games + Interactive" section (including that marker), and insert
    them into the `Bio` table.  

    Names are pulled from `data-title` attributes and inner text of `<span>`
    elements.  First/last names are split on the first space; characters without
    a space receive an empty last name.  Duplicate entries are ignored.
    """

    import re
    from sqlmodel import Session
    from sqlalchemy.exc import IntegrityError

    with open(html_path, "r", encoding="utf-8") as fp:
        text = fp.read()

    # limit to everything up to & including the Games+Interactive marker
    marker = "Databank | Games + Interactive"
    idx = text.find(marker)
    relevant = text if idx == -1 else text[: idx + len(marker)]

    candidates = set()

    # helper to determine if a captured string looks like a plausible personal name
    def plausible_name(s: str) -> bool:
        s = s.strip()
        if not s:
            return False
        lower = s.lower()
        # reject generic UI labels or repeated things
        bad_phrases = [
            "view all",
            "see all",
            "databank",
            "games + interactive",
            "all series",
            "browse databank",
            "runnable",
        ]
        if any(bp in lower for bp in bad_phrases):
            return False
        # reject names that are entirely uppercase (likely headings)
        if s.isupper():
            return False
        # reject strings containing digits
        if any(ch.isdigit() for ch in s):
            return False
        return True

    # capture data-title attributes
    for match in re.finditer(r'data-title="([^"]+)"', relevant):
        name = match.group(1).strip()
        if name and plausible_name(name):
            candidates.add(name)

    # capture <span>text</span> snippets (the ones holding visible names)
    for match in re.finditer(r"<span>\s*([^<]+?)\s*</span>", relevant):
        name = match.group(1).strip()
        if name and name not in candidates and plausible_name(name):
            candidates.add(name)

    # ensure the marker itself is included per instructions
    if plausible_name(marker):
        candidates.add(marker)

    # insert into database
    inserted = 0
    with Session(engine) as session:
        for full in sorted(candidates):
            parts = full.split(None, 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ""
            bio = Bio(first_name=first, last_name=last, series=series_value)
            session.add(bio)
            inserted += 1
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            # duplicates may have been attempted; ignore them

    return inserted
