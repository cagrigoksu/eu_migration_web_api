pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/cagrigoksu/eu_migration_web_api.git'
        DEV_BRANCH = 'dev'
        MAIN_BRANCH = 'main'
        VENV_DIR = 'venv'
        IMAGE_NAME = 'eu_migration'
        DOCKER_REGISTRY = 'localhost:5000'  // Local Docker registry (or Docker daemon)
    }

    stages {
        stage('Clone Repository') {
            steps {
                script {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: "*/${DEV_BRANCH}"]],
                        userRemoteConfigs: [[
                            url: REPO_URL,
                            credentialsId: 'github-token'
                        ]]
                    ])
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    sh '''
                    python3 -m venv ${VENV_DIR}
                    bash -c "source ${VENV_DIR}/bin/activate && pip install -r requirements.txt"
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    bash -c "source ${VENV_DIR}/bin/activate && pytest tests/"
                    '''
                }
            }
        }

        stage('Merge to Main') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD'),
                                     string(credentialsId: 'git-user-email', variable: 'GIT_EMAIL')]) {
                        sh '''
                        # Set up Git config
                        git config user.email "${GIT_EMAIL}"
                        git config user.name "Jenkins CI"

                        git reset --hard
                        git clean -fdx  # removes untracked files and directories
                        
                        # Fetch all branches from the remote
                        git fetch --all
                        
                        # Checkout the main branch
                        git checkout ${MAIN_BRANCH}
                        
                        # Merge the remote dev branch into main
                        git merge origin/${DEV_BRANCH}
                        
                        # Push the changes to the remote main branch with authentication
                        git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/cagrigoksu/eu_migration_web_api.git ${MAIN_BRANCH}
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                    docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} .
                    '''
                }
            }
        }

        stage('Push Docker Image to Local Docker Registry') {
            steps {
                script {
                    sh '''
                    docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}
                    '''
                }
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed!'
        }
        success {
            echo 'Code successfully merged to main and Docker image pushed!'
        }
    }
}
