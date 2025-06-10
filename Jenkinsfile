pipeline {
    agent any

    environment {
        DOCKER_HUB_USERNAME = 'saleemkhandev'
        TARGET_SERVER_IP = "54.169.213.2"
        SSH_KEY_ID = "devops-target-server-ssh-key"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_HUB_USERNAME/simple-flask-app:latest .'
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
                script {
                    sshCommand remote: [
                        // ADDED THIS LINE:
                        name: 'EC2-Target-Server', // You can give it any descriptive name
                        host: env.TARGET_SERVER_IP,
                        user: 'ec2-user', // *** IMPORTANT: Change to 'ubuntu' if your EC2 instance is Ubuntu, or another username if applicable ***
                        credentialsId: env.SSH_KEY_ID,
                        allowAnyHosts: true
                    ], command: """
                        set +e # Allow commands to fail without exiting the script immediately
                        
                        # Attempt to install Docker based on common Linux package managers
                        sudo yum install -y docker || sudo apt-get update && sudo apt-get install -y docker.io || true
                        
                        sudo systemctl start docker || true
                        sudo systemctl enable docker || true
                        
                        # Add current user (e.g., ec2-user or ubuntu) to the docker group to run docker commands without sudo
                        sudo usermod -a -G docker ec2-user || sudo usermod -a -G docker ubuntu || true # *** IMPORTANT: Adjust user here too ***
                        
                        set -e # Re-enable immediate exit on error for critical steps

                        # Stop and remove existing container and image to ensure a clean deployment
                        docker stop simple-flask-app-container || true
                        docker rm simple-flask-app-container || true
                        docker rmi ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest || true

                        # Pull the latest Docker image and run a new container
                        docker pull ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest
                        docker run -d -p 80:5000 --name simple-flask-app-container ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest
                    """
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
