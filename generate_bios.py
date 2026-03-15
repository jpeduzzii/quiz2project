import csv
from sqlmodel import Session, select
from models import Bio, engine

def generate_bios_from_csv(csv_path: str, series: str = "NHL"):
    """Read the CSV file, extract player names, split into first and last names,
    and insert Bio instances into the database. Skips duplicates."""

    with open(csv_path, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        with Session(engine) as session:
            for row in reader:
                full_name = row["Name"].strip()
                if not full_name:
                    continue
                parts = full_name.split(" ", 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ""
                
                # Check if already exists
                existing = session.exec(
                    select(Bio).where(
                        Bio.first_name == first_name,
                        Bio.last_name == last_name,
                        Bio.series == series
                    )
                ).first()
                if existing:
                    continue
                
                bio = Bio(
                    first_name=first_name, 
                    last_name=last_name, 
                    series=series,
                    team=row["Team"],
                    dob=row["DOB"],
                    position=row["Position"]
                )
                session.add(bio)
            session.commit()

if __name__ == "__main__":
    generate_bios_from_csv("top50_hockey.csv")