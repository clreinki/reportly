import configparser
from graph import Graph
from ips import IPS
import plotly.express as px
import pandas as pd


def main():
    print('''
   ____    U _____ u  ____    U  ___ u   ____      _____    _      __   __ 
U |  _"\ u \| ___"|/U|  _"\ u  \/"_ \/U |  _"\ u  |_ " _|  |"|     \ \ / / 
 \| |_) |/  |  _|"  \| |_) |/  | | | | \| |_) |/    | |  U | | u    \ V /  
  |  _ <    | |___   |  __/.-,_| |_| |  |  _ <     /| |\  \| |/__  U_|"|_u 
  |_| \_\   |_____|  |_|    \_)-\___/   |_| \_\   u |_|U   |_____|   |_|   
  //   \\_  <<   >>  ||>>_       \\     //   \\_  _// \\_  //  \\.-,//|(_  
 (__)  (__)(__) (__)(__)__)     (__)   (__)  (__)(__) (__)(_")("_)\_) (__) 

 know your user.
''')

    # Load settings
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']

    sus_user = input("Enter UserPrincipalName: ")
    start_date = input("Enter start date: ")
    end_date = input("Enter end date: ")
    output_file = input("Enter output path: ")
    if output_file == "":
        output_file = "report.html"
    graph: Graph = Graph(azure_settings, sus_user, start_date, end_date, output_file)
    greet_user(graph)
    create_final_report(graph)

def greet_user(graph: Graph):
    user = graph.get_user()
    print('Hello,', user['displayName'])
    print('Email:', user['mail'] or user['userPrincipalName'], '\n')

def display_access_token(graph: Graph):
    token = graph.get_user_token()
    print('User token:', token, '\n')

def call_audit_initiated(graph: Graph):
    audit = graph.get_audit_initiated()
    if audit == "This user has not performed any action.":
        return audit
    graph.create_graph_initiated()

def call_audit_target(graph: Graph):
    audit = graph.get_audit_target()
    if audit == "No operations have been performed on this user.":
        return audit
    graph.create_graph_target()

def call_signin(graph: Graph):
    audit_fail = graph.get_audit_signIn_failed()
    audit_success = graph.get_audit_signIn_success()
    if audit_fail == "No logs" and audit_success == "No logs":
        return "This user has not logged in."
    graph.create_graph_signin()

def get_sus_ips(graph: Graph):
    ips_dict = graph.get_ips()
    ips: IPS = IPS(ips_dict)
    ips.analyze_ips()
    sus_ips = ips.median_out_ips
    sus_ips_info = {}
    for ip in sus_ips:
        info = ips.return_ip_info(ip)
        sus_ips_info[ip] = info
    return sus_ips_info
    
def get_sigin_errors(graph:Graph):
    errors_list = graph.bad_sigin_errors()
    return errors_list

def create_final_report(graph:Graph):
    initiated = call_audit_initiated(graph)
    target = call_audit_target(graph)
    signin = call_signin(graph)
    ips = get_sus_ips(graph)
    signin_errors = get_sigin_errors(graph)
    graph.generate_report(initiated, target, signin, ips,signin_errors)
    print("Your report is ready!")

main()
