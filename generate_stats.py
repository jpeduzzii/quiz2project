import csv
from sqlmodel import Session, select
from models import Stats, engine

def generate_stats_from_csv(csv_path: str):
    """Read the CSV file, extract player stats, split names into first and last,
    and insert Stats instances into the database. Skips duplicates."""

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
                    select(Stats).where(
                        Stats.first_name == first_name,
                        Stats.last_name == last_name
                    )
                ).first()
                if existing:
                    continue
                
                stats = Stats(
                    first_name=first_name,
                    last_name=last_name,
                    gp=int(row["GP"]),
                    goals=int(row["G"]),
                    assists=int(row["A"]),
                    points=int(row["P"]),
                    pim=int(row["PIM"])
                )
                session.add(stats)
            session.commit()

if __name__ == "__main__":
    generate_stats_from_csv("top50_stats_after_pos.csv")