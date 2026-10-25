pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'ton-user-dockerhub'          // à remplacer
        IMAGE_NAME     = "${DOCKERHUB_USER}/flask-app"
        IMAGE_TAG      = "${BUILD_NUMBER}"
    }

    stages {

        stage('Code quality') {
            steps {
                sh '''
                    docker run --rm -v "$PWD":/src -w /src python:3.12-slim \
                      sh -c "pip install -q flake8 && flake8 ."
                '''
            }
        }

        stage('Unit tests') {
            steps {
                sh '''
                    docker run --rm -v "$PWD":/src -w /src python:3.12-slim \
                      sh -c "pip install -q -r requirements-dev.txt && pytest -v"
                '''
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG -t $IMAGE_NAME:latest .'
            }
        }

        stage('Test image') {
            steps {
                sh '''
                    docker rm -f test-app || true
                    docker run -d --name test-app -p 8081:8080 $IMAGE_NAME:$IMAGE_TAG
                    sleep 5
                    curl -fs http://localhost:8081 | grep -q "Hello World"
                    curl -fs http://localhost:8081/health | grep -q "ok"
                '''
            }
            post {
                always { sh 'docker rm -f test-app || true' }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push $IMAGE_NAME:$IMAGE_TAG
                        docker push $IMAGE_NAME:latest
                    '''
                }
            }
        }

        stage('Deploy staging') {
            steps {
                sshagent(credentials: ['aws-ssh-key']) {
                    sh '''
                        ansible-playbook -i ansible/inventory.ini ansible/deploy.yml \
                          --limit staging -e "image=$IMAGE_NAME:$IMAGE_TAG app_env=staging"
                    '''
                }
            }
        }

        stage('Validate staging') {
            steps {
                sh 'curl -fs http://STAGING_IP | grep -q "Hello World"'   // à remplacer
            }
        }

        stage('Deploy production') {
            when { branch 'main' }
            steps {
                input message: 'Déployer en production ?'
                sshagent(credentials: ['aws-ssh-key']) {
                    sh '''
                        ansible-playbook -i ansible/inventory.ini ansible/deploy.yml \
                          --limit production -e "image=$IMAGE_NAME:$IMAGE_TAG app_env=production"
                    '''
                }
            }
        }
    }

    post {
        always { sh 'docker logout || true' }
        success { echo "Pipeline OK : $IMAGE_NAME:$IMAGE_TAG" }
        failure { echo 'Pipeline en échec' }
    }
}
