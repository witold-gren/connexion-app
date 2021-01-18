#!/usr/bin/env groovy
import groovy.json.JsonOutput

// --- jenkins  ---
jenkinsSlave = "jenkins-slave"
jenkinsSSHId = "bdd06a12-8b87-45fe-820b-b4651ae96839"
jenkinsGithubCredentialsId = "GitHubCredentials"
// --- docker ---
dockerHost = "https://index.docker.io/v1/"
dockerRegistry = "witoldgren/${app}"
dockerFilePath = "backend/Dockerfile"
dockerContext = "."
dockerCredentialsId = "docker-hub"
dockerDBImage = "postgres:11.6-alpine"
// --- github ---
deployLink = "https://ci.example.com/job/${app}/parambuild?deploy=true"
// --- slack ---
slackChannel = "#notifications"
// Kubernetes
kubernetesDevEnv = "development"
kubernetesStgEnv = "staging"
kubernetesPrdEnv = "production"
service = "connexion-app"
deployJob = "../deploy-connexion-app"
ingressHost = "https://app.example.com"


properties([
    buildDiscarder(
        logRotator(
            daysToKeepStr: '3',
            numToKeepStr: '3'
        )
    ),
    parameters([
        booleanParam(
            name: "deploy",
            defaultValue: false,
            description: "Do you want to deploy?"
        )
    ])
])

timeout(20) {
    node(jenkinsSlave) {
        def repo = null
        def image = null

        stage('CleanWorkspace') {
            cleanWs()
        }

        stage("Build") {
            githubNotify (
                status: "PENDING",
                context: "1. ${STAGE_NAME}",
                description: "Building backend"
            )
            repo = checkout scm
            sh """
                echo ${repo.GIT_BRANCH} > backend/.appversion
                echo ${repo.GIT_COMMIT} > backend/.gitcommit
            """
            docker.withRegistry(dockerHost, dockerCredentialsId) {
                image = docker.build(
                    "${dockerRegistry}:${repo.GIT_COMMIT}",
                    "-f ${dockerFilePath} --pull ${dockerContext}"
                )
            }
            githubNotify (
                status: "SUCCESS",
                context: "1. ${STAGE_NAME}",
                description: "Backend build successfully"
            )
        }

        stage("Testing") {
            githubNotify (
                status: "PENDING",
                context: "2. ${STAGE_NAME}",
                description: "Testing backend"
            )
            repo = checkout scm

            docker.withRegistry(dockerHost, dockerCredentialsId) {
                docker.image(dockerDBImage).withRun('-e "POSTGRES_HOSTNAME=db"
                                                     -e "POSTGRES_PORT=5432"
                                                     -e "POSTGRES_DB=backend"
                                                     -e "POSTGRES_USER=backend"
                                                     -e "POSTGRES_PASSWORD=backend"') { c ->
                    image.inside('--link ${c.id}:db
                                  -e "FLASK_APP=wsgi:app"
                                  -e "FLASK_DEBUG=True"
                                  -e "POSTGRES_HOSTNAME=db"
                                  -e "POSTGRES_PORT=5432"
                                  -e "POSTGRES_DB=backend"
                                  -e "POSTGRES_USER=backend"
                                  -e "POSTGRES_PASSWORD=backend"') {
                        sh 'flask test'
                    }
                }
            }
            githubNotify (
                status: "SUCCESS",
                context: "2. ${STAGE_NAME}",
                description: "Testing backend successfully"
            )
        }

        stage("Push") {
            if(params.deploy || env.TAG_NAME != null || repo.GIT_BRANCH == "development" || repo.GIT_BRANCH == "master") {
                docker.withRegistry(dockerHost, dockerCredentialsId) {
                    image.push()

                    if(env.TAG_NAME != null){
                        image.push(env.TAG_NAME)
                    }

                    if(repo.GIT_BRANCH == "development"){
                        image.push('development')
                    }

                    if(repo.GIT_BRANCH == "master"){
                        image.push('latest')
                    }
                }
            }
        }

        stage("Deploy") {
            if(params.deploy || repo.GIT_BRANCH == "development" || env.TAG_NAME != null ) {
                def environment_env = null
                def dockerTag = repo.GIT_COMMIT

                if (repo.GIT_BRANCH == "development"){
                    environment_env = kubernetesDevEnv
                }

                if(env.TAG_NAME != null) {
                    environment_env = kubernetesStgEnv
                }

                if (environment_env) {
                    build(
                        job: deployJob,
                        parameters: [
                            string(name: 'environment', value: environment_env),
                            string(name: 'service', value: service),
                            string(name: 'version', value: repo.GIT_COMMIT)
                        ],
                        quietPeriod: 5,
                        wait: false
                    )
                }
            }

            if(env.CHANGE_ID != null && !params.deploy) {
                def body = [
                    body: """
                        #### PR built successfully
                        - Docker image [${dockerRegistry}:${repo.GIT_COMMIT}](https://hub.docker.com/r/${dockerRegistry}/tags/)
                        - [Deploy](${deployLink}) this change to [DEV](${ingressHost})
                    """.stripIndent()
                ]
                httpRequest (
                    url: "https://api.github.com/repos/${gitHubOrgName}/${app}/issues/${env.CHANGE_ID}/comments",
                    requestBody: JsonOutput.toJson(body),
                    authentication: jenkinsGithubCredentialsId,
                    httpMode: "POST",
                    contentType: "APPLICATION_JSON"
                )
            }
        }

        stage("Notification") {
            slackSend (
                channel: slackChannel,
                color: "good",
                message: [
                    "[<${env.RUN_DISPLAY_URL}|${env.BUILD_NUMBER}>] ",
                    "SUCCESS: *${app.toUpperCase()}* ",
                    "on branch *${repo.GIT_BRANCH}*"
                ].join("")
            )
        }
    }
}
