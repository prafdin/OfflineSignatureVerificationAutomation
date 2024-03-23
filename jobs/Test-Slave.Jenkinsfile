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
                def filesToArchive = ["params.yaml", "dvc.yaml", "repository_state.txt"]
                if (params.DVC_OVERRIDES) {
                    writeFile file: 'dvc_override_string.txt', text: params.DVC_OVERRIDES
                    filesToArchive.add("dvc_override_string.txt")
                }
                def gitRevision = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()

                archiveArtifacts artifacts: filesToArchive.join(","), followSymlinks: false

                sh("""\
                    dvc remote default local-cloud
                    dvc pull --allow-missing
                    dvc exp run --queue ${params.DVC_OVERRIDES}
                """.stripIndent())

                def countQueuedExperiments = sh(script: "dvc queue status", returnStdout: true).count("Queued")
                println("[INFO] Cound queued experiments: ${countQueuedExperiments}")
                sh("dvc queue start -j ${jobsCount}")

                waitUntil(quiet: true) {
                    sleep("90")
                    def statusCommandStdout = sh(script: "dvc queue status", returnStdout: true)

                    def runningExperiments = statusCommandStdout.count("Running")
                    def successfulExperiments = statusCommandStdout.count("Success")
                    def queuedExperiments = statusCommandStdout.count("Queued")
                    def failedExperiments = statusCommandStdout.count("Failed")
                    println("""\
                    Running experiments: ${runningExperiments}
                    Successful experiments: ${successfulExperiments}
                    Queued experiments: ${queuedExperiments}
                    Failed experiments: ${failedExperiments}""".stripIndent())

                    successfulExperiments + failedExperiments == countQueuedExperiments
                }
                sh("dvc exp show --json > raw_exp.json")
                sh("jq '[ .[] | select(.experiments != null ) | .experiments[] | { rev: \"${gitRevision}\", metrics: .revs[].data.metrics[][], params: .revs[].data.params[][]} ]' raw_exp.json > exp.json")
                archiveArtifacts artifacts: "exp.json", followSymlinks: false

                withCredentials([string(credentialsId: 'mongodb_connection_string', variable: 'connection_string')]) {
                    sh("mongoimport --jsonArray --file=exp.json --ssl --authenticationDatabase=db1 --sslCAFile=/home/jenkins/.mongodb/root.crt --db=db1 --collection=exps --uri=${connection_string}")
                }
            }
        }
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
    cleanWs()
}

