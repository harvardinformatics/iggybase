class WorkflowStatus:
    IN_PROGRESS = 2
    COMPLETE = 3
    FINAL = 4

class Timing:
    BEFORE = 'Before'
    AFTER = 'After'

class DatabaseEvent:
    INSERT = 'Insert'
    UPDATE = 'Update'

class ActionType:
    STEP = 1
    TABLE = 2
    ACTION_SUMMARY = 3
