class CwnAnnotationInfo:
    def __init__(self):
        self.annot = {}

    @property
    def author(self):
        return self.annot.get("author", "")
    
    @author.setter
    def author(self, x):
        self.annot["author"] = x

    @property
    def confidence(self):
        return self.annot.get("confidence", 1)
    
    @confidence.setter
    def confidence(self, x):
        if not (0 < x < 1):
            raise ValueError("confidence must be 0 < x < 1")
        else:
            self.annot["confidence"] = x

    @property
    def action(self):
        return self.annot.get("action", "create")

    @action.setter
    def action(self, x):
        if x not in ("create", "update", "delete"):
            raise ValueError("action must be one of create, update, delete")
        else:
            self.annot["action"] = x