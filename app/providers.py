class ScriptedModel:
    def decide(self, text):
        t = text.lower()
        if "return" in t:
            return {"intent": "return"}
        if "equipment" in t and "book" not in t and "reserve" not in t:
            return {"intent": "inventory"}
        return {"intent": "book"}
