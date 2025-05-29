pipeline {
    agent any

    environment {
        IMAGE_REPO_NAME = "shoppingapp"
        IMAGE_TAG = "${BUILD_NUMBER}"
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
        KUBE_YAML = "shoppingapp/backend/signin/signinsvc.yml"
        COMMIT_MESSAGE = "CI: Update image tag to ${IMAGE_TAG}"
        // JENKINSGITID = "jenkinsgit"
    }

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

        stage('Code Quality & Security Scan') {
            parallel {
                stage('Python Linting') {
                    steps {
                        sh '''    
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install black isort flake8 mypy bandit safety 


                            echo "Running Black formatter check (no cache)..."
                            black --check --diff shoppingapp/backend/signin/signin.py shoppingapp/backend/signup/signup.py || true

                            echo "Running isort import sorting check (no cache)..."
                            isort --check-only --diff shoppingapp/backend/signin/signin.py shoppingapp/backend/signup/signup.py || true

                            echo "Running Flake8 linting..."
                            flake8 shoppingapp/backend/signin/signin.py shoppingapp/backend/signup/signup.py --max-line-length=200 --extend-ignore=E203,W503 || true

                            echo "Running MyPy type checking..."
                            mypy shoppingapp/backend/signin/signin.py shoppingapp/backend/signup/signup.py --ignore-missing-imports --no-incremental || true

                            echo "Running Bandit security scan (no cache)..."
                            bandit -r . -f json -o bandit-report.json --exit-zero || true

                            echo "Running Safety dependency check (latest DB)..."
                            echo "Running Safety dependency check (latest DB)..."
                            safety check --output json > safety-report.json || true

                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
                        }
                    }
                }

                stage('Frontend Linting') {
                    steps {
                        sh '''       

                            npm install --save-dev eslint prettier
                            npx prettier --check .
                            npx prettier --write .
                           
                            echo "Running Prettier check without cache..."
                            prettier --check shoppingapp/frontend/src/ --no-cache || true
                            
                            echo "Running npm audit..."
                            npm audit --audit-level moderate --json > npm-audit.json || true

                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'eslint-report.json, npm-audit.json', allowEmptyArchive: true
                        }
                    }
                }

                stage('SonarQube Scan') {
                    steps {
                        echo 'Performing static code analysis with SonarQube...'
                        withSonarQubeEnv("${SONARQUBE_SERVER}") {
                            sh """
                                ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                                -Dsonar.projectKey=ShoppingApp \
                                -Dsonar.sources=. \
                                -Dsonar.exclusions=**/venv/**,**/__pycache__/**,**/*.pyc \
                                -Dsonar.sourceEncoding=UTF-8
                            """
                        }
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
            steps {
                script {
                    parallel(
                        'Build Signin Image': {
                            echo 'Building signin Docker image...'
                            sh "docker build --no-cache -t ${SIGNIN_DOCKERIMAGE_NAME} -f ${SIGNIN_DOCKERFILE} ."
                        },
                        'Build Signup Image': {
                            echo 'Building signup Docker image...'
                            sh "docker build --no-cache -t ${SIGNUP_DOCKERIMAGE_NAME} -f ${SIGNUP_DOCKERFILE} ."
                        },
                        'Build React Image': {
                            echo 'Building React frontend Docker image...'
                            sh "docker build --no-cache -t ${REACT_DOCKERIMAGE_NAME} -f ${REACT_DOCKERFILE} ."
                        }
                    )
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
                sh "docker push ${SIGNIN_DOCKERIMAGE_NAME}"
                sh "docker push ${SIGNUP_DOCKERIMAGE_NAME}"
                sh "docker push ${REACT_DOCKERIMAGE_NAME}"
            }
        }

        stage('Update Image Tag in K8S YAML') {
            steps {
                echo "Updating image tag to ${IMAGE_TAG} in ${KUBE_YAML}"
                    sh """
                    # Show current content
                    echo "Current content of ${KUBE_YAML}:"
                    cat ${KUBE_YAML}
            
                    # Create backup
                    cp ${KUBE_YAML} ${KUBE_YAML}.backup
            
                    # Update signin image tag
                    sed -i 's|aakashbodade/signin:[^[:space:]]*|aakashbodade/signin:${IMAGE_TAG}|g' ${KUBE_YAML}
            
                    # If you have other services in the same YAML file, update them too:
                    # sed -i 's|aakashbodade/signup:[^[:space:]]*|aakashbodade/signup:${IMAGE_TAG}|g' ${KUBE_YAML}
                    # sed -i 's|aakashbodade/react:[^[:space:]]*|aakashbodade/react:${IMAGE_TAG}|g' ${KUBE_YAML}
            
                    # Show updated content
                    echo "Updated content of ${KUBE_YAML}:"
                    cat ${KUBE_YAML}
            
                    # Show differences
                    echo "Changes made:"
                    diff ${KUBE_YAML}.backup ${KUBE_YAML} || true
            
                    # Verify the change was made
                    if grep -q "aakashbodade/signin:${IMAGE_TAG}" ${KUBE_YAML}; then
                        echo "✅ Image tag successfully updated to ${IMAGE_TAG}"
                    else
                        echo "❌ Failed to update image tag"
                        exit 1
                    fi
                    """
                }
        }

        stage('Commit & Push to GitHub') {
            steps {
                sshagent(credentials: ['jenkinsgit']) {
                    script {
                        // Ensure we're on the feature branch
                        sh """
                        git checkout feature || git checkout -b feature

                        git config user.name "aakashbodade"
                        git config user.email "aakashbodade1990@gmail.com"

                        git add shoppingapp/backend/signin/signinsvc.yml
                        git commit -m "${COMMIT_MESSAGE}" || echo "No changes to commit"

                        git push -o feature
                        """
                    }
                }
            }
        }
        

        // stage('Deploy Containers') {
        //     steps {
        //         echo 'Deploying Docker containers...'
        //         sh "docker run -d --restart=always -p 80:80 ${REACT_DOCKERIMAGE_NAME}"
        //         sh "docker run -d --restart=always -p 8001:8001 ${SIGNIN_DOCKERIMAGE_NAME}"
        //         sh "docker run -d --restart=always -p 8000:8000 ${SIGNUP_DOCKERIMAGE_NAME}"
        //     }
        // }
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
