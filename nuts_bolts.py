def enum(**enums: int):
    return type('Enum', (), enums)

program_flow = enum(TOOLCHANGE_ACK=0,
                    PROBE_START=1,
                    PROBE_COMPLETED=2,
                    PROBE_FIXTURE=3,
                    PROGRAM_COMPLETED = 30)

current_state = enum(STATE_ALARM=1,
              STATE_CYCLE=2,
              STATE_HOLD=3,
              STATE_TOOL_CHANGE=4,
              STATE_IDLE=5,
              STATE_HOMING=6,
              STATE_JOG=7,
              STATE_DEFAULT=254,)