import ciscoSupportAPIs as api
from dnacentersdk import api as dnacAPI
import csv
import easygui

def initialization():
    ciscoSupportAPI = api.API()
    ciscoSupportAPI.authenticate(
        APIkey = easygui.enterbox("Enter your API Key from https://apiconsole.cisco.com:"),
        APIsecret = easygui.enterbox("Enter your API Client Secret from https://apiconsole.cisco.com: ")
    )
    return ciscoSupportAPI

def obtain_sn2info(cisco, serialNumbers):
    result = cisco.getSN2InfoBySerial(serialNumbers)
    return result

def obtain_endOfSupport(cisco, deviceTypes):
    result = cisco.getEoxByModel(deviceTypes)
    return result

def getDevicesFromDNAC():
    dnac = dnacAPI.DNACenterAPI(
        base_url = easygui.enterbox("Enter the DNA Centre URL with NO trailing backslash: "),
        username = easygui.enterbox("Enter your DNA Centre username: "),
        password = easygui.enterbox("Enter your DNA Centre password: "),
        verify = False
    )

    runOffset = False; offsetVar = 0; allDevices = []
    for family in ["Switches and Hubs", "Routers"]:
        if runOffset:
            offsetVar += 500
            devices = dnac.devices.get_device_list(offset=offsetVar, family=family)
        else:
            devices = dnac.devices.get_device_list(family=family)
        allDevices += devices['response']
        if len(devices['response']) < 500:
            if family == "Routers":
                break
            else:
                continue
        else:
            runOffset = True

    return allDevices

def writeToFile(cisco, csvWriter, serialNumbers, devices, eoxData):
    sn2info = obtain_sn2info(cisco, serialNumbers)

    sn2infoData = {}
    for entry in sn2info['serial_numbers']:
        sn2infoData[entry['sr_no']] = entry

    for serial in serialNumbers:
        model = devices[serial]['platformId']
        if model in eoxData.keys():
            csvWriter.writerow({
                'Hostname': devices[serial]['hostname'],
                'Type': devices[serial]['type'],
                'Serial Number': serial,
                'Active Support Contract': sn2infoData[serial]['is_covered'],
                'BCF Contract Expiration Date': sn2infoData[serial]['coverage_end_date'],
                'External Announcement Date': eoxData[model]['EOXExternalAnnouncementDate']['value'],
                'Bulletin URL': eoxData[model]['LinkToProductBulletinURL'],
                'Vendor Sale End Date': eoxData[model]['EndOfSaleDate']['value'],
                'Vendor Support End Date': eoxData[model]['LastDateOfSupport']['value'],
                'Software Maintenance End Date': eoxData[model]['EndOfSWMaintenanceReleases']['value'],
                'Failure Analysis End Date': eoxData[model]['EndOfRoutineFailureAnalysisDate']['value'],
                'Service Attach End Date': eoxData[model]['EndOfSvcAttachDate']['value'],
                'Service Contract Renewal End Date': eoxData[model]['EndOfServiceContractRenewal']['value']
            })
        else:
            csvWriter.writerow({
                'Hostname': devices[serial]['hostname'],
                'Type': devices[serial]['type'],
                'Serial Number': serial,
                'Active Support Contract': sn2infoData[serial]['is_covered'],
                'BCF Contract Expiration Date': sn2infoData[serial]['coverage_end_date'],
                'External Announcement Date': "Not Announced"
            })

def getEoxData(cisco, models):
    eoxData = {}
    for i in range(0, len(models), 19):
        result = obtain_endOfSupport(cisco, models)
        for entry in result['EOXRecord']:
            eoxData[entry['EOLProductID']] = entry
    return eoxData

def main():    
    cisco = initialization()
    dnacDevices = getDevicesFromDNAC()
    
    devices = {}; deviceTypes = []

    for device in dnacDevices:
        model = device['platformId']
        if model:
            model = device['platformId'].strip()
            if "," in model:
                for platform in model.split(','):
                    if platform.strip() not in deviceTypes:
                        deviceTypes.append(platform.strip())
            else:
                if model not in deviceTypes:
                    deviceTypes.append(model)
        else:
            continue

    for device in dnacDevices:
        try:
            if "," in device['serialNumber']:
                serials = device['serialNumber'].split(",")
                for serial in serials:
                    devices[device[serial.strip()]] = device
            else:
                devices[device['serialNumber']] = device
        except TypeError:
            continue

    eoxData = getEoxData(cisco, deviceTypes)

    with open('Cisco EOL & EOS Dates.csv', 'w', newline='') as csvfile:
        fieldnames = [
            'Hostname',
            'Type',
            'Serial Number',
            'Active Support Contract',
            'BCF Contract Expiration Date',
            'External Announcement Date',
            'Bulletin URL',
            'Vendor Sale End Date',
            'Vendor Support End Date',
            'Software Maintenance End Date',
            'Failure Analysis End Date',
            'Service Attach End Date',
            'Service Contract Renewal End Date'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        serialNumbers = []
        for device in devices.keys():
            if device == None:
                continue
            serialNumbers.append(device)
            if len(serialNumbers) >= 19:
                writeToFile(cisco, writer, serialNumbers, devices, eoxData)
                serialNumbers = []
        if not len(serialNumbers) == 0:
            writeToFile(cisco, writer, serialNumbers, devices, eoxData) 
            serialNumbers = []

if __name__ == "__main__":
    main()