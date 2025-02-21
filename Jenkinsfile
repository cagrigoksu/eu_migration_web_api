pipeline {
    agent any

    environment {
        SOURCE_BRANCH = "dev"     
        TARGET_BRANCH = "main"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'SOURCE_BRANCH', url: 'https://github.com/cagrigoksu/eu_migration_web_api.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Linting') {
            steps {
                sh 'flake8 app.py'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest'
            }
        }

        stage('Merge Dev into Main & Push') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                        sh '''
                        git config --global user.email "cagrigoksu.ustundag@gmail.com"
                        git config --global user.name "Jenkins"
                        
                        git fetch origin

                        # Checkout main branch and merge dev into it
                        git checkout $TARGET_BRANCH
                        git merge origin/$SOURCE_BRANCH --no-edit

                        # Push changes to main branch
                        git push https://$GITHUB_TOKEN@github.com/YOUR_GITHUB_USERNAME/YOUR_REPO.git $TARGET_BRANCH
                        '''
                    }
                }
            }
        }
    }
}
