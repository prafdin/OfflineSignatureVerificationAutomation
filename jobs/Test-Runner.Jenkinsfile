import groovy.transform.Field

@Field
String testSlaveJobPath = "Test-Slave"
@Field
List<String> dvcConfigurationStrings = []

try {
    node('local-slave') {
        stage("Prepare configurations") {
            checkout scm
            dir("scripts") {
                sh "python3 generate_dvc_configs.py"
                dvcConfigurationStrings = readYaml(file: "dvc_configuration_strings.yaml")
            }
        }
        stage("Run slaves") {
            def slavesJobs = [:]
            dvcConfigurationStrings.eachWithIndex { configurationString, idx ->
                def jobParams = [string(name: 'PARAM', value: "${configurationString}")]
                slavesJobs["Job ${idx}"] = {
                    build(job: testSlaveJobPath, parameters: jobParams)
                }
            }

            parallel(slavesJobs)
        }

    }
}
finally {
    properties([
        parameters([
            gitParameter(
                name: 'CODE_BRANCH',
                quickFilterEnabled: false,
                selectedValue: 'NONE',
                sortMode: 'NONE',
                tagFilter: '*',
                type: 'PT_BRANCH',
                useRepository: 'https://github.com/prafdin/OfflineSignatureVerification.git',
                branch: '',
                branchFilter: 'origin/(.*)',
                defaultValue: 'master',
            ),
            text(
               name: 'TEST_CONFIG',
               description: """\
                Example:
                <pre>
                axis: 
                  - prepare.mode
                  - prepare.fixed_size
                  - featurization.method
                  - featurization.patterns_hist
                  - split.train_samples_per_user
                  - split.salt
                variants: 
                  - prepare.mode:
                      - default
                      - thinned
                  - prepare.fixed_size:
                      - "'300,400'"
                      - "'600,800'"
                  - featurization.method:
                      - lbp
                      - hog
                      - patterns_hist
                      - polinom_coefficients_hist
                  - featurization.patterns_hist: [4, 6, 8]
                  - split.train_samples_per_user: [6, 12, 18]
                  - split.salt: [22, 44]
                excludes: 
                  - prepare.mode:
                      - default
                    featurization.method:
                      - patterns_hist
                      - polinom_coefficients_hist
                </pre> 
               """.stripIndent()
            ),
        ])
   ])
}

