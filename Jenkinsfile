#!groovy

@Library('katsdpjenkins') _
katsdp.killOldJobs()
katsdp.setDependencies(['ska-sa/katsdptelstate/master'])
katsdp.standardBuild()
katsdp.mail('sdpdev+katsdpservices@sarao.ac.za')
