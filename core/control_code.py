from enum import Enum

class ControlCode(Enum):
    Download_Ready = 0
    Download_Queueing = 1
    Download_Start = 2
    Download_Before_Complete = 4
    Download_After_Ready = Download_Before_Complete
    Download_After_Start = 6
    Download_After_Complete = 8
    Download_Complete = Download_After_Complete
    Data_Not_Found = 10
    WorkSuspend = 11
    WorkSuspenedDone = 12
    InternalEngineException = 80
    WorkDone = 100