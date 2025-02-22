pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/cagrigoksu/eu_migration_web_api.git'
        DEV_BRANCH = 'dev'
        MAIN_BRANCH = 'main'
        VENV_DIR = 'venv'
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
                    source ${VENV_DIR}/bin/activate
                    pip install -r requirements.txt
                    pip install pytest
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    source ${VENV_DIR}/bin/activate
                    pytest tests/
                    '''
                }
            }
        }

        stage('Merge to Main') {
            steps {
                script {
                    sh '''
                    git config user.email "cagrigoksu.ustundag@gmail.com"
                    git config user.name "Jenkins CI"
                    git checkout ${MAIN_BRANCH}
                    git merge ${DEV_BRANCH}
                    git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/cagrigoksu/eu_migration_web_api.git ${MAIN_BRANCH}
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
            echo 'Code successfully merged to main!'
        }
    }
}
