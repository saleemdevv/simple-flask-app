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
        GITHUB_PAT_ID = "github-pat-credential"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', credentialsId: env.GITHUB_PAT_ID, url: "https://github.com/${env.DOCKER_HUB_USERNAME}/simple-flask-app.git"
            }
        }

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
            agent any // <--- Keep 'agent any' here, as this stage will run on the main Jenkins agent
            steps {
                // <--- sshAgent MOVED HERE, INSIDE steps block
                sshAgent([env.SSH_KEY_ID]) { // This block injects the SSH key
                    script {
                        def remote = [:]
                        remote.name = 'web-server'
                        remote.host = env.TARGET_SERVER_IP
                        remote.user = 'ec2-user' // Default user for Amazon Linux 2
                        remote.allowAnyHosts = true // WARNING: In production, configure known_hosts properly for security

                        sshCommand remote: remote, command: """
                            # Ensure docker is installed (should be from user_data, but good as fallback)
                            sudo yum install -y docker || true
                            sudo systemctl start docker || true # Start docker if not running
                            sudo systemctl enable docker || true # Enable docker on boot
                            sudo usermod -a -G docker ec2-user || true # Add ec2-user to docker group if not already

                            # Clean up previous container and image to ensure fresh deployment
                            docker stop simple-flask-app-container || true
                            docker rm simple-flask-app-container || true
                            docker rmi ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest || true # Use env variable here

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
            cleanWs() // Clean up workspace after build
        }
        failure {
            echo "Pipeline failed."
            // Add notifications here if needed (e.g., email, Slack)
        }
        success {
            echo "Pipeline succeeded!"
            // Add notifications here if needed
        }
    }
}
