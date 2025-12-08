# app/agents/member_agent.py
class MemberAgent:
    """Handles member ID input + validation."""

    def ask_member_id(self, state: dict) -> dict:
        member_id = input("Please enter your member id: ").strip()
        return {"member_id": member_id}

    def validate_member_id(self, state: dict) -> dict:
        member_id = (state.get("member_id") or "").strip()
        valid = len(member_id) >= 5

        if valid:
            print("member id validated")
        else:
            print("Invalid member id, it should be at least 5 characters")

        return {"valid": valid}
