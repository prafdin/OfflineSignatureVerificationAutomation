import groovy.transform.Field

@Field
String sourceRepositoryUrl = "https://github.com/prafdin/OfflineSignatureVerification.git"
@Field
String testSlaveJobPath = "Test-Slave"
@Field
List<String> dvcConfigurationStrings = []


node('jenkins-container-slave') {
    try {
        stage("Prepare configurations") {
            checkout scm
            dir("scripts") {
                if (params.TEST_CONFIG) {
                    customTestConfig = readYaml(text: params.TEST_CONFIG)
                    testsConfig = readYaml(file: "tests.yaml")
                    testsConfig['tests']['sanity_check'] = customTestConfig
                    sh("rm -f tests.yaml")
                    writeYaml data: testsConfig, file: "tests.yaml"
                }
                sh "python3 generate_dvc_configs.py"
                dvcConfigurationStrings = readYaml(file: "dvc_configuration_strings.yaml")
            }
        }
        stage("Run slaves") {
            def slavesJobs = [:]
            dvcConfigurationStrings.eachWithIndex { configurationString, idx ->
                def jobParams = [
                    string(name: 'SOURCE_BRANCH', value: params.SOURCE_BRANCH),
                    string(name: 'DVC_OVERRIDES', value: configurationString),
                ]
                slavesJobs["Job ${idx}"] = {
                    build(job: testSlaveJobPath, parameters: jobParams)
                }
            }

            parallel(slavesJobs)
        }
    }
    finally {
        properties(
            [
                parameters(
                    [
                        listGitBranches(
                            branchFilter: 'refs/heads/(.*)',
                            credentialsId: '',
                            defaultValue: 'master',
                            listSize: '0',
                            name: 'SOURCE_BRANCH',
                            quickFilterEnabled: true,
                            remoteURL: sourceRepositoryUrl,
                            selectedValue: 'DEFAULT',
                            sortMode: 'NONE',
                            tagFilter: '*',
                            type: 'PT_BRANCH'
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
                    ]
                )
            ]
        )
        cleanWs()
    }
}

