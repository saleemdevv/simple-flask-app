pipeline {
    agent any
    environment {
        // Your Docker Hub username
        DOCKER_HUB_USERNAME = 'saleemkhandev'
        // Target server IP address from your Terraform output
        TARGET_SERVER_IP = "122.248.206.50" // Ensure this matches your target EC2 IP
        // This must match the ID you set for the SSH private key in Jenkins Credentials
        SSH_KEY_ID = "devops-target-server-ssh-key"
        // Credentials ID for your GitHub Personal Access Token (PAT)
        // We'll remove this as the repo is public and implicit checkout works
        // GITHUB_PAT_ID = "github-pat-credential" // This line will be removed
    }

    stages {
        // REMOVED: The 'Checkout Code' stage is now removed.
        // Jenkins automatically checks out the code configured in the job's SCM settings
        // at the very beginning of the pipeline run.

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_HUB_USERNAME/simple-flask-app:latest .'
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-password-credential', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    sh 'docker push $DOCKER_HUB_USERNAME/simple-flask-app:latest'
                }
            }
        }

        stage('Deploy to EC2') {
            agent any
            steps {
                sshAgent([env.SSH_KEY_ID]) {
                    script {
                        def remote = [:]
                        remote.name = 'web-server'
                        remote.host = env.TARGET_SERVER_IP
                        remote.user = 'ec2-user'
                        remote.allowAnyHosts = true

                        sshCommand remote: remote, command: """
                            sudo yum install -y docker || true
                            sudo systemctl start docker || true
                            sudo systemctl enable docker || true
                            sudo usermod -a -G docker ec2-user || true

                            docker stop simple-flask-app-container || true
                            docker rm simple-flask-app-container || true
                            docker rmi ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest || true

                            docker pull ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest
                            docker run -d -p 80:5000 --name simple-flask-app-container ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
        failure {
            echo "Pipeline failed."
        }
        success {
            echo "Pipeline succeeded!"
        }
    }
}
