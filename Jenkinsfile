pipeline {
    environment {
        IMAGE_REPO_NAME = "shoppingapp"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        AWS_DEFAULT_REGION = "ap-south-1"
        AWS_ACCOUNT_ID = "120569600896"
        REACT_DOCKERFILE = "shoppingapp/frontend/Dockerfile"
        SIGNIN_DOCKERFILE = "shoppingapp/backend/signin/Dockerfile"
        SIGNUP_DOCKERFILE = "shoppingapp/backend/signup/Dockerfile"
        REACT_DOCKERIMAGE_NAME = "aakashbodade/react:${IMAGE_TAG}" 
        SIGNIN_DOCKERIMAGE_NAME = "aakashbodade/signin:${IMAGE_TAG}"
        SIGNUP_DOCKERIMAGE_NAME = "aakashbodade/signup:${IMAGE_TAG}"
        DOCKER_CREDENTIALS = credentials('DOCKERHUB_CREDENTIALS')
        SONARQUBE_SERVER = 'SonarQube'
        SONAR_SCANNER_HOME = tool 'SonarQubeScanner'
    }
    agent any
    options {
        ansiColor('xterm') // Add color to logs for better readability
        buildDiscarder(logRotator(numToKeepStr: '5')) // Limit build history retention
        disableConcurrentBuilds() // Prevent overlapping builds
        timestamps() // Timestamp logs for better traceability
    }
    stages {
        stage('Clone Repository') {
            steps {
                echo 'Cloning Git repository...'
                checkout scm
            }
        }

        stage('Run SonarQube Analysis') {
            steps {
                script {
                    echo 'Performing static code analysis with SonarQube...'
                    withSonarQubeEnv(SONARQUBE_SERVER) {
                        sh "${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                            -Dsonar.projectKey=ShoppingApp \
                            -Dsonar.sources=. \
                            -Dsonar.language=py,js \
                            -Dsonar.sourceEncoding=UTF-8"
                    }
                }
            }
        }
        
        stage('Check Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build Signin Image') {
                    steps {
                        echo 'Building signin Docker image...'
                        sh "docker build --no-cache -t ${SIGNIN_DOCKERIMAGE_NAME} -f ${SIGNIN_DOCKERFILE} ."
                    }
                }
                stage('Build Signup Image') {
                    steps {
                        echo 'Building signup Docker image...'
                        sh "docker build --no-cache -t ${SIGNUP_DOCKERIMAGE_NAME} -f ${SIGNUP_DOCKERFILE} ."
                    }
                }
                stage('Build React Image') {
                    steps {
                        echo 'Building React frontend Docker image...'
                        sh "docker build --no-cache -t ${REACT_DOCKERIMAGE_NAME} -f ${REACT_DOCKERFILE} ."
                    }
                }
            }
        }

        stage('DockerHub Login') {
            steps {
                echo 'Logging in to DockerHub...'
                sh "docker login -u '${DOCKER_CREDENTIALS_USR}' -p '${DOCKER_CREDENTIALS_PSW}'"
            }
        }

        stage('Push Docker Images') {
            steps {
                echo 'Pushing Docker images to DockerHub...'
                script {
                    sh "docker push ${SIGNIN_DOCKERIMAGE_NAME}"
                    sh "docker push ${SIGNUP_DOCKERIMAGE_NAME}"
                    sh "docker push ${REACT_DOCKERIMAGE_NAME}"
                }
            }
        }

        stage('Deploy Containers') {
            steps {
                echo 'Deploying Docker containers...'
                script {
                    sh "docker run -d --restart=always -p 80:80 ${REACT_DOCKERIMAGE_NAME}"
                    sh "docker run -d --restart=always -p 8001:8001 ${SIGNIN_DOCKERIMAGE_NAME}"
                    sh "docker run -d --restart=always -p 8000:8000 ${SIGNUP_DOCKERIMAGE_NAME}"
                }
            }
        }
    }
    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Investigate and resolve issues.'
        }
    }
}
