#!groovy

@Library('katsdpjenkins') _
katsdp.killOldJobs()
katsdp.setDependencies(['ska-sa/katsdpdockerbase/python2'])
katsdp.standardBuild(python2: true, python3: true, katsdpdockerbase_ref: 'python2')
katsdp.mail('sdpdev+katsdpservices@ska.ac.za')
