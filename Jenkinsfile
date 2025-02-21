pipeline {
    agent any

    environment {
        SOURCE_BRANCH = "dev"     
        TARGET_BRANCH = "main"
    }

    stages {
        stage('Clone Repository') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                        sh '''
                        git clone -b $SOURCE_BRANCH https://$GITHUB_TOKEN@github.com/cagrigoksu/eu_migration_web_api.git repo
                        cd repo
                        '''
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r repo/requirements.txt'
            }
        }

        stage('Linting') {
            steps {
                sh 'flake8 repo/app.py'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest repo/'
            }
        }

        stage('Merge Dev into Main & Push') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                        sh '''
                        cd repo
                        git config --global user.email "cagrigoksu.ustundag@gmail.com"
                        git config --global user.name "Jenkins"

                        git fetch origin
                        git checkout -B $TARGET_BRANCH origin/$TARGET_BRANCH

                        git merge origin/$SOURCE_BRANCH --no-edit

                        git push https://$GITHUB_TOKEN@github.com/cagrigoksu/eu_migration_web_api.git $TARGET_BRANCH
                        '''
                    }
                }
            }
        }
    }
}
