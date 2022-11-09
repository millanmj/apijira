from platform import processor
from flask import Flask, jsonify, request
from flask_cors import CORS
import jira
import requests
from requests.auth import HTTPBasicAuth
import json
# import the installed Jira library
from jira import JIRA
from datetime import datetime


#Agregar pre y post condiciones
def MapeoGerencia(gerente:str)->str:
    gerencia: str= ''
    if ('Ariel Cosentino' == gerente):
        gerencia = "10034" #Gerencia de red de Sucursales
        #gerencia = "10051" #Gerencia de red de Sucursales
    elif ('Gisela Marino comercial' == gerente):
        gerencia = "10030" #'Gerencia Comercial
        #gerencia = "10047" #'Gerencia Comercial
    elif ('Alejandro Bermann' == gerente):        
        gerencia = "10028" #Gerencia de AFyL
        #gerencia = "10045" #Gerencia de AFyL
    elif ('5cb0e51cfb6145589296296a' == gerente):
        #gerencia = "10046" #'Gerencia de Tecnología
        gerencia = "10029" #'Gerencia de Tecnología
    elif ('Carmen Rojas' == gerente):
        gerencia = "10031" #Compliance y Procesos
        #gerencia = "10048" #Compliance y Procesos
    elif ('Solange Altilio' == gerente):
        gerencia = "10036" #Investigación y Capacitación'
        #gerencia = "10053" #Investigación y Capacitación'    
    elif ('Ignacio Stella personas' == gerente):
        gerencia = "10035" #Comunicación Institucional
        #gerencia = "10050" #Comunicación Institucional
    elif ('Mariela Luna riesgo' == gerente):        
        gerencia = "10032"
        #gerencia = 'Gerencia de Riesgo'
    else: gerencia = "10029" #Si es otra asignar tecno
    
    return str(gerencia)

def filtrarProyectos(data: list) -> list:
    newName: str = ''
    lekeadData: list = []
    names: list = ['GDD', 'GT', 'GP0007', 'RDG', 'SP000BN']
    for project in data:
        for name in names:
            if (project.get('key')== name):
                if ( (project.get('name').find('-')) != -1):
                    indice = project.get('name').find('')
                    newName = project.get('name').split('-')[1][1:]
                    
                    project['name'] = newName.capitalize()
                else: project['name'] = project['name'].capitalize()  
                lekeadData.append(project)
    return lekeadData

    
         


app = Flask(__name__)
cors = CORS(app)
#dashboard/10001/items/customfield_10055/properties/value
@app.route('/Test',methods=['GET'])
def TestHeader() -> json:      
    response: json= requests.request("GET", url+"users/search", headers= headers, auth= auth)
    data: dict= response.json()    
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
  
    return jsonify(data)

#Buscar todos los eventos (no entiendo bien que son) devuelve una lista issues
@app.route('/Events', methods=['GET'])
def GetEvents() -> json:
    response: json= requests.request("GET", url+"events", headers= headers, auth= auth)
    data: dict= response.json()    
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
  
    return jsonify(data)

#Buscar requerimiento por ID
@app.route('/Issue/<id_requerimiento>', methods=['GET'])
def GetIssueForId(id_requerimiento) -> json:
    response: json= requests.request("GET", url+ "issue/"+ id_requerimiento, headers= headers, auth= auth)
    data: dict= response.json()    
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    
    return jsonify(data)    

#En este modulo voy a probar utilizar la libreria de JIRA de python
#Traer todos los requerimientos de un tablero por nombre de proyecto (BACK,DEV,TST,STG,PROD,etc)
#singleIssue.key = Nombre del requerimiento
#singleIssue.fields.summary = Descripción del requerimiento
#singleIssue.fields.reporter.displayName= Creador del requerimiento

#Json example body: {'key':'nombre del proyecto'}
@app.route('/Issues', methods=['GET'])
def GetIssuesInformation() -> json:   
    Issues: list= []
    # DEJAMOS COMENTANDAS LAS SIGUIENTES 2 LINEAS PARA PROBAR EL GET DESDE EL CLIENTE
    # info: dict= {"key": request.json["key"]} 
    # project_name:str= info["key"]
    project_name: str= 'GDD'
    Issue: dict= {}
    jiraOptions ={'server': "https://"+domain+".atlassian.net"}
    #Autenticación en jira a través de la libreria de python
    jira = JIRA(options=jiraOptions, basic_auth=(mail, tokenId))
    #Busco todos los requerimientos creado por nombre de proyecto
    for singleIssue in jira.search_issues(jql_str='project = '+ project_name):       
        Issue= {'key':singleIssue.key,
                'summary': singleIssue.fields.summary,
                'description': singleIssue.fields.description,
                'nameReporter': singleIssue.fields.reporter.displayName,
                'assignee': singleIssue.fields.assignee
                }

        Issues.append(Issue)
        data= Issues
        for i in Issues:
            print(Issue)     
    
    return jsonify(data)    

#Crear requerimiento con la libreria de Jira

@app.route('/CreateIssue', methods=['POST'])
def CreateNewIssue() -> json:   
    
    jiraOptions ={'server': "https://"+domain+".atlassian.net"}
    jira = JIRA(options=jiraOptions, basic_auth=(mail, tokenId))
    
    print('DATA',request.json)
    issue_dict = {
        "project": {"key": request.json['key']},
        "summary": request.json['summary'],
        "description": 'Rol: '+ request.json['managment']+ '\n'+ 'Funcionalidad: '+request.json['description']
                       +'\n'+ 'Beneficio: '+ request.json['impact'] + '\n Enlace a la Documentación: '
                       + request.json['attached'],        
        "priority": {"id":request.json['priority']},  

         #VARIABLES DE AMBIENTE DE PRODUCCION
        # "issuetype": {"id":"10001"},
        # #"customfield_10052": {"value": request.json['impact']},
        # "customfield_10038":str(request.json['finalDate'][0:10]),        
        # "customfield_10039":str(request.json['normativeDate'][0:10]),
        # "customfield_10003":[{'accountId':str(request.json['approvers'])}],        
        # "customfield_10054":[{'id':MapeoGerencia(str(request.json['approvers']))}]
   

        #VARIABLES DE AMBIENTE DE DESARROLLO
        "issuetype": {"name": request.json['type']},
        # # "customfield_10053": {"value": request.json['impact']},
         
       
        "customfield_10050":[{'accountId':str(request.json['approvers'])}]        
        # "customfield_10055":{'id':MapeoGerencia(str(request.json['approvers']))}
    }
    
    if "finalDate" in request.json:
        issue_dict['customfield_10061']= str((request.json['finalDate'][0:10]))
   
    if "normativeDate" in request.json:
        issue_dict['customfield_10062']=str((request.json['normativeDate'][0:10]))
    print(issue_dict)

 
    # print(issue_dict["priority"], "esto es la prioridad parseada")

    print("esto es el nuevo incidente creado",issue_dict)
    new_issue = jira.create_issue(fields=issue_dict)

    #jira.add_attachment(issue=new_issue, attachment='C:/Users/Colaborador/Documents/logo-icon.png')

    print("este es el nuevo incidente", new_issue)
   
    data = issue_dict
    print(type(new_issue))
    print("esto es el response", new_issue.fields.issuelinks)
    link = 'https://'+ domain + '.atlassian.net/browse/' + new_issue.key
    return jsonify({"link":link, "key":new_issue.key})




@app.route('/GetAllProjects', methods=['GET'])
def GetProjects() -> json:   
    
    jiraOptions ={'server': "https://"+domain+".atlassian.net"}
    jira = JIRA(options=jiraOptions, basic_auth=(mail, tokenId))
    data: list=[]
    projectInfo: dict = {'name': str, 'key': str}
    projects = jira.projects()
   
    for project in projects:
        projectInfo['key']= (project.key)
        projectInfo['name']= (project.name)
        data.append(projectInfo)
        projectInfo = {}

    #data = filtrarProyectos(data)
    sorted(data, key=lambda name: max(list(name.values())))
    return jsonify({"projects":data})



# 


# Crear requerimiento
# @app.route('/CrearRequerimiento', methods=['POST'])
# def CreateIssue() -> json:
#     domain: str="tst-pm"
#     mail: str= "mmillan@provinciamicrocreditos.com"
#     tokenId: str= "w09WsgcMifr600iYMYkO768D"
#     idDashboard: int= 10000

#     auth = HTTPBasicAuth(mail, tokenId)
#     headers = {"Accept": "application/json","Content-Type":"application/json"}
#     path: str= ""
#     url: str= "https://"+domain+".atlassian.net/rest/api/3/"
    
#     payload = json.dumps({
    
#      "update": {
    
#     },
#     "fields": {
#        "project": {"key": request.json['key']},
#        "summary": request.json['summary'],
#        "description": request.json['description'],
#        "issuetype": {"name": request.json['issuetype']}
#     }})    
    
#     response = requests.request("POST", url+ "issue",data=payload, headers= headers, auth= auth)
#     # response = requests.post(url+"issue", headers= headers, data=payload,auth= auth)
    
#     data: dict= response.json()

#     return data
 

   

if __name__ == "__main__":
        
    
   
    domain: str="tst-pm"
    mail: str= "mmillan@provinciamicrocreditos.com"
    tokenId: str= "w09WsgcMifr600iYMYkO768D"

    # domain: str="provinciamicroempresas"
    # mail: str="dacuna@provinciamicrocreditos.com"
    # tokenId: str= "lOkCELYRGDTEQGsBHULSC7BF"

    idDashboard: int= 10000

    auth = HTTPBasicAuth(mail, tokenId)
    headers = {"Accept": "application/json","Content-Type":"application/json"}
    path: str= ""
    url: str= "https://"+domain+".atlassian.net/rest/api/3/"

    #PATHS de consultas generales
    #applicationrole 
    #announcementBanner 
    #dashboard
    #issue/createmeta
    #atlassian.net/rest/api/2/issue/TSTAPI-3

   
    app.run(debug= True, port = 4000)
