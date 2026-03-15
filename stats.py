from sqlmodel import Session
from models import Stats, engine
from generate_bio_instances import generate_bio_list

with Session(engine) as session:
    player_info = generate_bio_list()
    session.add_all(player_info)
    session.commit()