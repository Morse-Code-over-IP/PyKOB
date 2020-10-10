"""
MIT License

Copyright (c) 2020 PyKOB - MorseKOB in Python

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Recorder class

Records wire and local station information for analysis and playback.
Plays back recorded information.

The information is recorded in packets in a JSON structure that includes:
1. Timestamp
2. Source (`local`/`wire`)
3. Station ID
4. Wire Number
5. Code type
6. Code Sequence (key timing information)

Though the name of the class is `recorder` it is typical that a 'recorder' can also
play back. For example, a 'tape recorder', a 'video casset recorder (VCR)',
a 'digital video recorder' (DVR), etc. can all play back what they (and compatible
devices) have recorded. This class is no exception. It provides methods to play back
recordings in addition to making recordings.

"""
import json
import time
from datetime import datetime
from pykob import config, kob

@unique
class PlaybackState(IntEnum):
    """
    The current state of recording playback.
    """
    idle = 0
    playing = 3
    paused = 4

def get_timestamp():
    """
    Return the current  millisecond timestamp.

    Return
    ------
    ts : number
        milliseconds since the epoc
    """
    ts = int(time.time() * 1000)
    return ts
    
class Recorder:
    """
    Recorder class provides functionality to record and playback a code stream.
    """

    def __init__(self, target_file_path=None, source_file_path=None, \
            station_id="", wire=-1, station_id_callback=None, wire_callback=None):
        self.__target_file_path = target_file_path
        self.__source_file_path = source_file_path
        self.__station_id = station_id
        self.__wire = wire
        self.__station_id_callback = station_id_callback
        self.__wire_callback = wire_callback

    @property
    def station_id_callback(self):
        """
        The callback called for each station ID played.
        """
        return __station_id_callback

    @station_id_callback.setter
    def station_id_callback(self, station_id_callback):
        """
        Set the Station ID callback called for each station ID while the 
        recording is played back.
        """
        self.__station_id_callback = station_id_callback

    @property
    def wire_callback(self):
        return self.__wire_callback
    
    @wire_callback.setter
    def wire_callback(self, wire_callback):
        self.__wire_callback = wire_callback

    @property
    def source_file_path(self):
        """
        The path to the source file used to play back a code sequence stored in PyKOB JSON format.
        """
        return self.__source_file_path

    @source_file_path.setter
    def source_file_path(self, path):
        """
        Set the source file path.
        """
        self.__source_file_path = path

    @property
    def target_file_path(self):
        """
        The path to the target file used to record a code sequence in PyKOB JSON format.
        """
        return self.__target_file_path

    @target_file_path.setter
    def target_file_path(self, target_file_path):
        """
        Set the target file path to record to.
        """
        self.__target_file_path = target_file_path

    @property
    def station_id(self):
        """
        The Station ID.
        """
        return self.__station_id

    @station_id.setter
    def station_id(self, station_id):
        """
        Set the Station ID.
        """
        self.__station_id = station_id

    @property
    def wire(self):
        """
        The Wire.
        """
        return self.__wire

    @wire.setter
    def wire(self, wire):
        """
        Set the Wire.
        """
        self.__wire = wire

    def record(self, code, source):
        """
        Record a code sequence in JSON format with additional context information.
        """
        timestamp = get_timestamp()
        data = {
            "ts":timestamp,
            "w":self.__wire,
            "s":self.__station_id,
            "o":source,
            "c":code
        }
        with open(self.__target_file_path, "a+") as fp:
            json.dump(data, fp)
            fp.write('\n')

    def playback(self, list_data=False, max_silence=0, speed_factor=100, 
            code_callback=None, station_callback=None, wire_callback=None):
        """
        Play a recording to the configured sounder.
        """
        lts = -1 # Keep the last timestamp
        lstation = None
        lwire = None
        with open(self.__source_file_path, "r") as fp:
            for line in fp:
                data = json.loads(line)
                code = data['c']
                ts = data['ts']
                wire = data['w']
                station = data['s']
                if not wire == lwire:
                    lwire = wire
                    if wire_callback:
                        wire_callback(wire)
                if not station == lstation:
                    lstation = station
                    if station_callback:
                        station_callback(station)
                if lts < 0:
                    lts = ts
                if list_data:
                    dateTime = datetime.fromtimestamp(ts / 1000.0)
                    dateTimeStr = str(dateTime.ctime()) + ": "
                    print(dateTimeStr, line, end='')
                if code == []:  # Ignore empty code packets
                    continue
                self.__wire = data['w']
                self.__station_id = data['s']
                codePause = -code[0] / 1000.0  # delay since end of previous code sequence and beginning of this one
                # For short pauses (< 1 sec), `KOB.sounder` can handle them more precisely.
                # However the way `KOB.sounder` handles longer pauses, although it makes sense for
                # real-time transmissions, is flawed for playback. Better to handle long pauses here.
                # A pause of 0x3777 ms is a special case indicating a discontinuity and requires special
                # handling in `KOB.sounder`.
                if codePause > 1.0 and codePause < 32.767:
                    # For very long delays, sleep a maximum of `max_silence` seconds
                    pause = round((ts - lts)/1000, 4)
                    if max_silence > 0 and pause > max_silence:
                        print("Realtime pause of {} seconds being reduced to {} seconds".format(pause, max_silence))
                        pause = max_silence
                    time.sleep(pause)
                    code[0] = -1  # Remove pause from code sequence since it's already handled
                if speed_factor != 100:
                    sf = 1.0 / (speed_factor / 100.0)
                    for c in code:
                        if c < 0 or c > 2:
                            c = round(sf * c)
                if code_callback:
                    self.code_callback(code)
                lts = ts

    def resume_playback():
        """
        Resume a paused playback.

        The `playback` method must have been called to set up the necessary state.
        """



"""
Test code
"""
if __name__ == "__main__":
    # Self-test
    from pykob import morse

    test_target_filename = "test." + str(get_timestamp()) + ".json"
    myRecorder = Recorder(test_target_filename, test_target_filename, station_id="Test Recorder", wire=-1)
    mySender = morse.Sender(20)

    # 'HI' at 20 wpm as a test
    print("HI")
    codesequence = (-1000, +2, -1000, +60, -60, +60, -60, +60, -60, +60,
            -180, +60, -60, +60, -1000, +1)
    myRecorder.record(codesequence, kob.CodeSource.local)
    # Append more text to the same file
    for c in "This is a test":
        codesequence = mySender.encode(c, True)
        myRecorder.record(codesequence, kob.CodeSource.local)
    print()
    # Play the file
    myKOB = kob.KOB(port=None, audio=True)
    myRecorder.playback(myKOB)

