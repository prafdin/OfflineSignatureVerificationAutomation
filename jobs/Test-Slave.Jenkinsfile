import groovy.transform.Field

@Field
String sourceRepositoryUrl = "https://github.com/prafdin/OfflineSignatureVerification.git"
@Field
int jobsCount = 3

try {
    node('jenkins-slave') {
        stage("Check parameters") {
            def requiredParameters = [params.SOURCE_BRANCH]
            if (!requiredParameters.every()) {
                error("Not all mandatory parameters are specified")
            }
        }
        stage("Run dvc") {
            def sourceCodeDir = "src"
            checkout scmGit(
                branches: [
                    [name: params.SOURCE_BRANCH]
                ],
                extensions: [
                    [$class: 'RelativeTargetDirectory', relativeTargetDir: sourceCodeDir],
                ],
                userRemoteConfigs: [
                    [url: sourceRepositoryUrl]
                ]
            )
            dir(sourceCodeDir) {
                archiveArtifacts artifacts: 'params.yaml,dvc.yaml', followSymlinks: false
                if (params.DVC_OVERRIDES) {
                    writeFile file: 'dvc_override_string.txt', text: params.DVC_OVERRIDES
                }
                writeFile file: 'repository_state.txt', text: sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                archiveArtifacts artifacts: '*.txt', followSymlinks: false

                sh("""\
                    dvc remote default local-cloud
                    dvc pull
                """.stripIndent())

                if (params.DVC_OVERRIDES) {
                    sh("""\
                        dvc exp run --queue ${params.DVC_OVERRIDES}
                    """.stripIndent())
                }
                else {
                    sh("""\
                        dvc exp run --queue
                    """.stripIndent())
                }
                def countQueuedExperiments = sh(script: "dvc queue status", returnStdout: true).count("Queued")
                sh("dvc queue start -j ${jobsCount}")

                waitUntil(initialRecurrencePeriod: 15000) {
                    def statusCommandStdout = sh(script: "dvc queue status", returnStdout: true)

                    statusCommandStdout.count("Success") + statusCommandStdout.count("Failed") == countQueuedExperiments
                }
            }
        }

        cleanWs()
    }
}
finally {
    properties([
        parameters([
            string(name: 'SOURCE_BRANCH', defaultValue: 'master'),
            string(
                name: 'DVC_OVERRIDES',
                defaultValue: '',
                description: """\
                Value of this parameter will be added after command:
                <pre>
                dvc exp run --queue -j N \$DVC_OVERRIDES
                </pre>                    
                Example:<br/>
                <pre>
                -S prepare.mode="default,thinned" -S prepare.fixed_size="'600,800','300,400'"
                </pre>
                """.stripIndent()
            ),
        ])
    ])
}

