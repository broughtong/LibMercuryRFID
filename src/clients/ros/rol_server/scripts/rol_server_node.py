#!/usr/bin/env python

import yaml
import rospy
import operator
from std_msgs.msg import String
from rol_server.srv import findObject, findObjectRequest, findObjectResponse


# Node class.
class ProbHandler():
    def __init__(self,top,obj):
        self.object=obj
        self.topic=top
        rospy.Subscriber(self.topic, String, self.probCallback)

    def probCallback(self,data):
        self.rawData=data.data

    def getProbs(self):
        splitData=self.rawData.split(',')
        self.probs = splitData[1::2]
        self.locations = splitData[::2]

        probDict=dict(zip(self.locations,self.probs))
        return probDict

class rol_server():


    def performLoc(self,findObjectReq):
        rospy.logdebug("Received service request.")
        rospy.logdebug("Action: %s", findObjectReq.action)
        rospy.logdebug("Payload: %s",findObjectReq.payload)

        if   findObjectReq.action is 'list':
            ans=self.performListAct(findObjectReq.payload)
        elif findObjectReq.action is 'find':
            ans=self.performFindAct(findObjectReq.payload)
        elif findObjectReq.action is 'accurate_find':
            ans=self.performAcFindAct(findObjectReq.payload)
        else:
            ans=self.createErrorResponse('Unknown action: '+ findObjectReq.action)
        return ans

    def performListAct(self,payload):
        '''
        Returns a list of objects, locations or sublocations available
        :param payload: 'objects' , 'locations' or 'sublocations'
        :return: filled srv response with proper list
        '''

        if   payload is 'objects':
            ans=self.createOkResponse(self.objectsList)
        elif payload is 'locations':
            ans=self.createOkResponse(self.locationsList)
        elif payload is 'sublocations':
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
            probs = self.getProbs(obj)
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


    def getProbs(self,obj):
        ans = ''

        probDict=(self.probHandlerList[obj]).getProbs()
        fullProbs = sorted(probDict.items(), key=operator.itemgetter(1))

        for z,p in fullProbs:
            if z in self.locationsList:
                ans=ans+z+str(p)
        return ans

    def getAcProbs(self,obj):
        ans=[]

        #get prob dict
        probDict = (self.probHandlerList[obj]).getProbs()

        #get most probable location
        bestProb=0
        bestRegion=''
        for reg,prob in probDict:
            if bestProb<prob:
                bestProb=prob
                bestRegion=reg

        #get a probabilities dict from this location
        bestSublocationsDict=dict()
        for bestRegion in self.yDict['Regions']:
            if bestRegion.has_key('subregions'):
                for subR in bestRegion['subregions']:
                    bestSublocationsDict[subR['name']]=probDict[subR['name']]/bestProb

        #parse a list of relative probabilities
        if not bestSublocationsDict:
            ans.append(bestRegion)
            ans.append(str(bestProb))
            ans=','.join(ans)
        else:
            sortedList = sorted(bestSublocationsDict.items(), key=operator.itemgetter(1))
            ans=','.join([i for sub in sortedList for i in sub])


        return ans

    def rosSetup(self):
        self.probHandlerList=dict()
        self.regions_file=''
        listOfTopics = rospy.get_published_topics()

        for tup in listOfTopics:
            if ('probs' in tup[0]) and ('std_msgs/String' in tup[1]):
                foundTopic=tup[0]
                nodeName=foundTopic[0:-5]
                objectName=rospy.get_param(nodeName+'object')
                prH = ProbHandler(foundTopic,objectName)
                self.probHandlerList[objectName]=(prH)
                self.objectsList.append(objectName)
                if len(self.regions_file)==0:
                    self.regions_file=rospy.get_param(nodeName + 'regions_file')

    def probCallback(self,data):
        probsString=data.data

    def loadLocations(self):
        self.yDict = dict()
        with open(self.regions_file) as stream:
            try:
                yDict=(yaml.load(stream))
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

        # ros set-up: find out tracked objects, subscribe to their probs...
        self.rosSetup()

        # get list of map locations and sublocations
        self.loadLocations()


        self.s=rospy.Service('rol_server', findObject, self.performLoc)

        rospy.loginfo("Ready...")
        rospy.spin()


# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('rol_server')

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        r_s = rol_server()
    except rospy.ROSInterruptException: pass
