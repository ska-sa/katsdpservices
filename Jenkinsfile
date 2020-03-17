#!groovy

@Library('katsdpjenkins') _
katsdp.killOldJobs()
katsdp.standardBuild(python2: false, python3: true)
katsdp.mail('sdpdev+katsdpservices@ska.ac.za')
