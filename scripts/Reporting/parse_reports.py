import json
import os
from typing import Dict
from loguru import logger

def get_positives(report: Dict) -> int:
    """
    Get number of positive

    Args:
        report (Dict): dictionary with reporting data

    Returns:
        int: number of positive reports
    """
    return report['data']['attributes']['last_analysis_stats']['malicious']

def get_strings(report: Dict) -> list:
    if 'androguard' in report['data']['attributes'].keys():
        return report['data']['attributes']['androguard']['StringsInformation']
    else:
        return None

def check_string(strings: list) -> bool:
    """
    Check presence of payloads in extracted strings

    Args:
        report (Dict): dictionary with reporting data

    Returns:
        bool: True/False if payloads are present/not present
    """

    payload1 = """'59.183.111.96:57926/i*d*58.47.106.191:51900/bin.sh*d*117.213.92.42:56783/Mozi.m'"""
    payload2 = '''methode.setAccessible(true);methode.invoke(null,this.b,this.c,this.a);ag.g[8]="rrqnDG4dja7Ga5ZdAuD77CY";ag.g[9]="xodOhs"'''

    payloads = [p.replace("'", "") for p in payload1.split('*d*')] + [payload2]
    for p in payloads:
        if strings is not None:
            if p in strings:
                return True
            else:
                return False
        else:
            return None

def get_mal_av(report: Dict) -> list:
    """
    Get positive AV

    Args:
        report (Dict): dictionary with reporting data

    Returns:
        list: positive AV
    """
    positives = list()
    last_analysis = report['data']['attributes']['last_analysis_results']
    for av, value in last_analysis.items():
        if value['category'] == 'malicious':
            positives.append(av)
    
    return positives


def main():
    report_path = os.path.join('./vt_reports')
    for report in os.listdir(report_path):
        with open(os.path.join(report_path, report)) as fp:
            r = json.load(fp)
        # print("Positives: ", get_positives(r['virustotal_scan']))
        # print("String: ", get_strings(r['virustotal_scan']))
        positives = get_positives(r['virustotal_scan'])
        positives_av = None
        if positives > 0:
            positives_av = get_mal_av(r['virustotal_scan'])
        logger.info(f"""Report: {report}\n\tPositives: {positives}\n\tPresence: {check_string(get_strings(r['virustotal_scan']))}\n\tAV: {positives_av}""")



if __name__ == "__main__":
    logger.remove()
    logger.add('VT_parser_report.log', format='{time:MM-DD HH:mm}|{message}', level="INFO")
    main()