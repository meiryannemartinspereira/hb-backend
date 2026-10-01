from domain.entities.participant import Participant, ParticipantType
from domain.entities.owner import Owner


participant = Participant(
    participant_id="P001",
    participant_type=ParticipantType.INDIVIDUAL,
    name="Rosa",
    tax_id="12345678900"
)

owner = Owner(
    owner_id="O001",
    participant_id=participant.participant_id,
    name=participant.name
)

print(participant)
print(owner)