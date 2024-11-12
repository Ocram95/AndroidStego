import vt
import json
from typing import Dict, Optional
from utils import sha256sum
import os
from loguru import logger
from pprint import pformat


class VirusTotal:
    
    def __init__(self, vt_key: str, save_path:str):
        """
        Parameters
        ----------
        vt_key : str
            virus total api key
        save_path: str
            path where to save the reports
        """
        logger.remove()
        def make_filter(name):
            def filter(record):
                return record["extra"].get("name") == name
            return filter
        logger.add('VT_logger.log', format='{time:MM-DD HH:mm}|{message}', level="INFO", 
                    filter=make_filter("VT_logger"))
        super().__init__()
        self.__vt_session = vt.Client(vt_key)
        self.__save_path = save_path
        self.__logger = logger.bind(name="VT_logger")

    
    @staticmethod
    def __get_positives(report: Dict) -> int:
        return report['data']['attributes']['last_analysis_stats']['malicious']
    
    def __get_report(self, sha256_hash: str) -> Optional[dict]:
        """
        Get report of the file identified by sha256 hash

        Parameters
        ----------
        sha256_hash : str
            hash of the file to search

        Returns
        -------
        Optional[dict]
            None or Dict of report
        """
        try:
            report = self.__vt_session.get_json(f'/files/{sha256_hash}')
            return report
        except vt.error.APIError:
            return None

    def __scan_apk_file(self, apk_file_path: str) -> Dict:
        self.__logger.info(f'Scanning file "{apk_file_path}"')
        # sha256_hash = sha256sum(apk_file_path)
        sha256_hash = apk_file_path.split(os.path.sep)[-1].replace('.apk', '')
        
        report = self.__get_report(sha256_hash)

        if report is not None:
            return report
        
        with open(apk_file_path, 'rb') as f:
            self.__logger.info(f"Uploading '{apk_file_path}' to VT ...")
            analysis = self.__vt_session.scan_file(f, wait_for_completion=True)
            assert analysis.status == "completed"
        
        report = self.__get_report(sha256_hash)
        if report is None:
            raise Exception(
                f'Error while retrieving scan for file "{apk_file_path}"'
            )
        return report

    def analyse_apk(self, apk_file_path: str):
        
        try:
            if not os.path.isfile(apk_file_path):
                raise FileNotFoundError(
                    'Apk was not found!'
                )
            report = self.__scan_apk_file(apk_file_path)
            self.__logger.info(
                f"Apk {apk_file_path} scan result {self.__get_positives(report)} positives"
            )
            sha256_hash = apk_file_path.split(os.path.sep)[-1].replace('.apk', '')
            report_path = os.path.join(self.__save_path, f'{sha256_hash}.json')
            with open(report_path, 'w') as f_report:
                f_report.write(
                    json.dumps(
                        {"virustotal_scan": report}, 
                        indent=2,
                        sort_keys=True
                    )
                )
        except Exception as e:
            self.__logger.error("Error during Virus Total analysis: {0}".format(e))
            raise

        finally:
            self.__vt_session.close()