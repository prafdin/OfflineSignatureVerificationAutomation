import groovy.transform.Field

@Field
String testSlaveJobPath = "Test-Slave"
@Field
List<String> dvcConfigurationStrings = []

node('master') {
    stage("Prepare configurations") {
        checkout scm
        dir("scripts") {
            sh "python3 generate_dvc_configs.py"
            dvcConfigurationStrings = readYaml("dvc_configuration_strings.yaml")
        }
    }
    stage("Run slaves") {
        def slavesJobs = [:]
        dvcConfigurationStrings.each { configurationString, idx ->
            def jobParams = [string(name: 'PARAM', value: "${configurationString}")]
            slavesJobs["Job ${idx}"] = {
                build(job: testSlaveJobPath, parameters: jobParams)
            }
        }

        parallel(slavesJobs)
    }
}
