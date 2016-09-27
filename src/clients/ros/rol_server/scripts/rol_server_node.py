#!/usr/bin/env python

import yaml
import rospy
import operator
from std_msgs.msg import String
#from rol_server.srv import findObject, findObjectRequest, findObjectResponse
from hmi_bridge.srv import findObject, findObjectRequest, findObjectResponse


# Node class.
class ProbHandler():
    def __init__(self,top,obj):
        self.object=obj
        self.topic=top
        self.lastLoc=''
        rospy.Subscriber(self.topic, String, self.probCallback)

    def probCallback(self,data):
        self.rawData=data.data

    def setLocations(self, locs):
        self.locs=locs

    def getLastLoc(self):
        return self.lastLoc

    def getProbs(self):

        try:
            splitData=self.rawData.split(',')
            self.probs = splitData[3::2]
            self.locs = splitData[2::2]
            self.lastLoc=splitData[0]
        except AttributeError:
            self.probs=[0]*len(self.locs)


        probDict=dict(zip(self.locs, self.probs))

        return probDict

class rol_server():

    def percentFormat(self, strNum):

        return  '{:.2f}'.format(100. *float( strNum))


    def performLoc(self,findObjectReq):
        receivedAction = str.lower(findObjectReq.action)
        receivedPayload = str.lower(findObjectReq.payload)
        rospy.logdebug("Received service request.")
        rospy.logdebug("Action: %s", receivedAction)
        rospy.logdebug("Payload: %s",receivedPayload)

        if   receivedAction== 'list':
            ans=self.performListAct(receivedPayload )
        elif receivedAction== 'find':
            ans=self.performFindAct(receivedPayload )
        elif receivedAction== 'accurate_find':
            ans=self.performAcFindAct(receivedPayload )
        else:
            ans=self.createErrorResponse('Unknown action: '+ findObjectReq.action)

        self.rol_pub.publish(ans.response)

        return ans

    def performListAct(self,payload):
        '''
        Returns a list of objects, locations or sublocations available
        :param payload: 'objects' , 'locations' or 'sublocations'
        :return: filled srv response with proper list
        '''

        if   payload == 'objects':
            ans=self.createOkResponse(self.objectsList)
        elif payload == 'locations':
            ans=self.createOkResponse(self.locationsList)
        elif payload == 'sublocations':
            ans=self.createOkResponse(self.sublocationsList)
        else:
            ans=self.createErrorResponse('Unknown payload for list action:'+ payload)
        return ans

    def performAcFindAct(self, obj):
        if obj in self.objectsList:
            probs = self.getAcProbs(obj)
            ans = self.createOkResponse(probs)
        else:
            ans = self.createErrorResponse('Unknown object to accurately find:' + obj)

        return ans

    def performFindAct(self, obj):

        if obj in self.objectsList:
            probs = self.getObjectProbs(obj)
            ans=self.createOkResponse(probs)
        else:
            ans = self.createErrorResponse('Unknown object to find:' + obj)

        return ans

    def createOkResponse(self, data):
        '''
        Embeds a sequence of strings to a ROL srv response
        :param data: sequence to be joined and stored in srv response
        :return: filled srv response
        '''

        separator = ","

        ans = findObjectResponse()
        ans.response = separator.join(data)
        ans.wasOk = True
        ans.feedback = ''

        return ans

    def createErrorResponse(self, data):
        '''
        Returns a srv response describing an error
        :param data: error description
        :return: filled srv response
        '''

        ans = findObjectResponse()
        ans.response = ''
        ans.wasOk = False
        ans.feedback = data

        return ans


    def getObjectProbs(self,obj):
        ans = []

        pH=self.probHandlerList[obj]
        probDict=pH.getProbs()
        fullProbs = sorted(probDict.items(), key=operator.itemgetter(1), reverse=True)

        lastL=pH.getLastLoc()
        if (lastL != ''):
            ans.append(lastL)
            ans.append('-1')
        for z,p in fullProbs:
            if z in self.locationsList:
                ans.append(z)
                ans.append(self.percentFormat(p))
        return ans

    def getAcProbs(self,obj):
        ans=[]

        #get prob dict
        probDict = (self.probHandlerList[obj]).getProbs()

        #get most probable location
        fullProbs = sorted(probDict.items(), key=operator.itemgetter(1), reverse=True)

        bestRegion,bestProb = fullProbs[0]

        rospy.logdebug('Region is:   ' + bestRegion)
        rospy.logdebug('Probability: ' + str(bestProb))

        #get a probabilities dict from this location
        bestSublocationsDict=dict()
        for reg in self.yDict['Regions']:
            if reg.has_key('subregions'):
                if reg['name'] == bestRegion:
                    for subR in reg['subregions']:
                        rospy.logdebug('Subregion is: '+subR['name'])
                        rospy.logdebug('Probability:  ' + probDict[subR['name']])
                        rospy.logdebug('Relative Pr:  ' + probDict[subR['name']])
                        bestSublocationsDict[subR['name']]=str(float(probDict[subR['name']])/float(bestProb))

        #parse a list of relative probabilities
        if not bestSublocationsDict:
            ans.append(bestRegion)
            ans.append(self.percentFormat(bestProb))
            #ans=','.join(ans)
        else:
            sortedList = sorted(bestSublocationsDict.items(), key=operator.itemgetter(1),reverse=True)
            for bestRegion,bestProb in sortedList:
                ans.append(bestRegion)
                ans.append(self.percentFormat(bestProb))
                #ans=[i for tup in sortedList for i in tup]


        return ans

    def rosSetup(self):
        self.probHandlerList=dict()
        self.regions_file=''
        self.rolTopic=rospy.get_param('rolTopic','rol_requests')

        listOfTopics = rospy.get_published_topics()

        for tup in listOfTopics:
            if ('probs' in tup[0]) and ('std_msgs/String' in tup[1]):
                foundTopic=tup[0]
                nodeName=foundTopic[0:-5]
                if len(self.regions_file)==0:
                    self.regions_file=rospy.get_param(nodeName + 'regions_file')
                    self.loadLocations()

                objectName=rospy.get_param(nodeName+'object')
                self.objectsList.append(objectName)

                prH = ProbHandler(foundTopic,objectName)
                prH.setLocations(self.locationsList)
                self.probHandlerList[objectName] = (prH)

    def probCallback(self,data):
        probsString=data.data

    #called by rossetup, to load locations list.
    def loadLocations(self):
        self.yDict = dict()
        with open(self.regions_file) as stream:
            try:
                self.yDict=(yaml.load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        for region in self.yDict['Regions']:
            self.locationsList.append(region['name'])
            if region.has_key('subregions'):
                for subR in region['subregions']:
                    self.sublocationsList.append(subR['name'])


    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        rospy.loginfo("Advertising RFID object location service ")


        #create some storage atributes
        self.objectsList = []
        self.locationsList=[]
        self.sublocationsList = []

        # get parameters from ros: find out tracked objects, locations, subscribe to their probs trackers...
        self.rosSetup()

        # create publisher for service requests
        self.rol_pub = rospy.Publisher(self.rolTopic, String, queue_size=10)


        # start service callback
        self.s=rospy.Service('rol_server', findObject, self.performLoc)


        rospy.loginfo("Ready...")
        rospy.spin()


# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('rol_server', log_level=rospy.DEBUG)

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        r_s = rol_server()
    except rospy.ROSInterruptException: pass
