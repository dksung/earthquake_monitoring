import logging
import logging.handlers
import os
import inspect
from datetime import datetime

class LogHandler:
    def __init__(self, log_path):
        """
        LogHandler class init

        :param log_path: Log file path
        """
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(asctime)s  %(message)s',
            # datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(os.path.join(log_path, f'{datetime.now().strftime("%Y_%m%d")}_eq_log.txt')),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger()
        self.job_cnt = 1

    def write_log(self, msg, level='info', count=False):
        """
        Log 생성

        :param str msg: Log Message
        :param str level: Log Level (critical / error / info)
        """
        msg = msg.replace('\n', '\t')
        if count is True:
            msg = ('[%d] ' % self.job_cnt) + msg
            self.job_cnt += 1
        _, filename, line_number, function_name, _, _ = inspect.stack()[1]
        message = '%-26s  %-23s  %-4s  %s' % (os.path.basename(filename), function_name, line_number, msg)
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'critical':
            self.logger.critical(message)
        else:
            self.logger.debug(message)