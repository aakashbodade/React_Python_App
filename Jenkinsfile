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
        buildDiscarder(logRotator(numToKeepStr: '5'))
        disableConcurrentBuilds()
        timestamps()
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
                echo 'Performing static code analysis with SonarQube...'
                withSonarQubeEnv(env.SONARQUBE_SERVER) {
                    sh "${env.SONAR_SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=ShoppingApp \
                        -Dsonar.sources=. \
                        -Dsonar.sourceEncoding=UTF-8"
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
            steps {
                script {
                    parallel(
                        'Build Signin Image': {
                            echo 'Building signin Docker image...'
                            sh "docker build --no-cache -t ${env.SIGNIN_DOCKERIMAGE_NAME} -f ${env.SIGNIN_DOCKERFILE} ."
                        },
                        'Build Signup Image': {
                            echo 'Building signup Docker image...'
                            sh "docker build --no-cache -t ${env.SIGNUP_DOCKERIMAGE_NAME} -f ${env.SIGNUP_DOCKERFILE} ."
                        },
                        'Build React Image': {
                            echo 'Building React frontend Docker image...'
                            sh "docker build --no-cache -t ${env.REACT_DOCKERIMAGE_NAME} -f ${env.REACT_DOCKERFILE} ."
                        }
                    )
                }
            }
        }

        stage('DockerHub Login') {
            steps {
                echo 'Logging in to DockerHub...'
                sh "docker login -u '${env.DOCKER_CREDENTIALS_USR}' -p '${env.DOCKER_CREDENTIALS_PSW}'"
            }
        }

        stage('Push Docker Images') {
            steps {
                echo 'Pushing Docker images to DockerHub...'
                sh "docker push ${env.SIGNIN_DOCKERIMAGE_NAME}"
                sh "docker push ${env.SIGNUP_DOCKERIMAGE_NAME}"
                sh "docker push ${env.REACT_DOCKERIMAGE_NAME}"
            }
        }

        stage('Deploy Containers') {
            steps {
                echo 'Deploying Docker containers...'
                sh "docker run -d --restart=always -p 80:80 ${env.REACT_DOCKERIMAGE_NAME}"
                sh "docker run -d --restart=always -p 8001:8001 ${env.SIGNIN_DOCKERIMAGE_NAME}"
                sh "docker run -d --restart=always -p 8000:8000 ${env.SIGNUP_DOCKERIMAGE_NAME}"
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


