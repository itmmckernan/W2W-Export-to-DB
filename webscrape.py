from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime
import json
import configparser

config = configparser.ConfigParser()

config.read('config.ini')

username = config['Login']['Username']

password = config['Login']['Password']

export_script = "return JSON.stringify(Array.from(document.getElementsByClassName('maintab bwgtcolors')[0].children).slice(1).reduce((r, v, i, o) => !(i % 2)? [...r, [Array.from(o[i].firstChild.firstChild.children).map(e => e.getAttribute('onclick') === null ? NaN : new Date(e.getAttribute('onclick').split('=').slice(-1)[0].split('\\'')[0])), Array.from(o[i+1].firstChild.firstChild.children)]] : r, []).map(e => e[0].map((f, i) => [f, e[1][i]])).flat().filter(e => !isNaN(e[0]) && e[1].getAttribute('class') == 'weekpubback').map(z => [{'Date': z[0], 'Shifts': Array.from(z[1].children).filter(e => e.nodeName != 'IMG').reduce((p, e, i, o) => e.getAttribute('class') == 'skh'? p : [...p, ...Array.from(e.children).filter(u => u.nodeName == 'DIV').map(q => [{'Position': o[o.map(e => e.getAttribute('class')).lastIndexOf('skh', i)].innerText, 'Employee': q.children[0].firstChild.nodeName == 'B' ? q.children[0].firstChild.innerText.split(' (deleted)')[0] : 'UNASSIGNED', 'Start Time': new Date((e.firstChild.data.split(' - ')[0].slice(0, -2).includes(':') ? e.firstChild.data.split(' - ')[0].slice(0, -2) : e.firstChild.data.split(' - ')[0].slice(0, -2) + ':00') + ' ' + e.firstChild.data.split(' - ')[0].slice(-2) + ' ' + z[0].toDateString().slice(4)), 'End Time': new Date((e.firstChild.data.split(' - ')[1].slice(0, -2).includes(':') ? e.firstChild.data.split(' - ')[1].slice(0, -2) : e.firstChild.data.split(' - ')[1].slice(0, -2) + ':00') + ' ' + e.firstChild.data.split(' - ')[1].slice(-2) + ' ' + z[0].toDateString().slice(4)), 'Location': q.children[0].firstChild.nodeName == 'B' ? q.children[0].firstChild.nextSibling != null? q.children[0].firstChild.nextSibling.data.slice(3) : 'UNASSIGNED' : 'UNASSIGNED', 'Deleted': (q.children[0].firstChild.nodeName == 'B' ? q.children[0].firstChild.innerText : '').includes(' (deleted)') }][0])], [])}][0]).map(a => a['Shifts'].map(e => e['Start Time'] > e['End Time']? {...e, 'End Time': new Date(e['End Time'].setDate(e['End Time'].getDate() +1))}: e)).flat())"

driver = webdriver.Edge()
driver.get('https://www6.w2w.com/cgi-bin/w2wFF.dll/empfullschedule?SID=17239793214110&lmi=&View=Month#')
WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
driver.execute_script(
    f'console.log("run"); document.getElementById("username").value = "{username}"; document.getElementById("password").value = "{password}"; document.querySelector("body > div.container-fluid > div > div > div > div > form > div:nth-child(12) > button").click();')
WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

def fixup(e):
    if e["Employee"] == "UNASSIGNED":
        e["Employee"] = None
    if e["Location"] == "UNASSIGNED":
        e["Location"] = None
    e["Start Time"] = datetime.strptime(e["Start Time"], '%Y-%m-%dT%H:%M:%S.000Z')
    e["End Time"] = datetime.strptime(e["End Time"], '%Y-%m-%dT%H:%M:%S.000Z')
    return e

def fetch_month(month=datetime.now().month, year=datetime.now().year):
    driver.execute_script(f'ReplWin("empfullschedule","&View=Month&date={month}/1/{year}")')
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    out = driver.execute_script(export_script)
    out_obj = json.loads(out)
    return [fixup(e) for e in out_obj]