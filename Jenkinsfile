#!groovy

@Library('katsdpjenkins') _
katsdp.killOldJobs()
katsdp.standardBuild(python2: true, python3: true)
katsdp.mail('bmerry@ska.ac.za')
