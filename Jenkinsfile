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
        DOCKER_USERNAME = credentials('DOCKERHUB_USERNAME')
        DOCKER_PASSWORD = credentials('DOCKERHUB_PASSWORD')
    }
    agent any
    stages {
        stage ('Cloning git repository'){
            steps {
                checkout scm
            }
        }

        stage ('Building Docker Images'){
            parallel {
                stage('Building signin docker image'){
                    steps{
                        script{
                            sh "docker build -t ${SIGNIN_DOCKERIMAGE_NAME} -f ${SIGNIN_DOCKERFILE} ."
                        }
                    }
                }
                stage('Building signup docker image'){
                    steps{
                        script{
                            sh "docker build -t ${SIGNUP_DOCKERIMAGE_NAME} -f ${SIGNUP_DOCKERFILE}"
                        }
                    }
                }
                stage('Building react docker image'){
                    steps{
                        script{
                            sh "docker build -t ${REACT_DOCKERIMAGE_NAME} -f ${REACT_DOCKERFILE}"
                        }
                    }
                }
            }
        }
        stage ("Dockerhub login"){
            steps{
                script{
                    sh "docker login --username ${DOCKER_USERNAME} --password-stdin"
                }
            }
        }
        stage ("Push Image to docker hub"){
            script{
                sh "docker push ${SIGNIN_DOCKERIMAGE_NAME}"
                sh "docker push ${SIGNUP_DOCKERIMAGE_NAME}"
                sh "docker push ${REACT_DOCKERIMAGE_NAME}"
            }
        }
    }
}