pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: kaniko
                image: gcr.io/kaniko-project/executor:debug
                command: ["/busybox/cat"]
                tty: true
                volumeMounts:
                  - name: docker-config
                    mountPath: /kaniko/.docker
              volumes:
                - name: docker-config
                  secret:
                    secretName: docker-hub-secret
                    items:
                      - key: .dockerconfigjson
                        path: config.json
            '''
        }
    }
    
    parameters {
        string(name: 'TAG_VERSION', defaultValue: 'v1', description: 'Version Tag')
    }

    environment {
        // แก้เป็นชื่อ Docker Hub คุณ
        DOCKER_IMAGE = 'konipn/devops-lab' 
        // แก้เป็น Link Repo GitHub คุณ
        GIT_REPO = 'https://github.com/KoniPN/devops-lab-project.git'
    }

    stages {
        stage('Build & Push Image') {
            steps {
                container('kaniko') {
                    // Kaniko คือตัว Build Docker Image ใน K8s ที่ง่ายและปลอดภัยกว่า Docker-in-Docker
                    sh """
                    /kaniko/executor \
                        --context `pwd` \
                        --destination ${DOCKER_IMAGE}:${TAG_VERSION} \
                        --build-arg APP_VERSION=${TAG_VERSION}
                    """
                }
            }
        }

        stage('Update Manifest (GitOps)') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-login', passwordVariable: 'GIT_PASS', usernameVariable: 'GIT_USER')]) {
                    sh """
                        git config user.email "kong.18th@gmail.com"
                        git config user.name "KoniPN"
                        
                        # ดึงโค้ดล่าสุด
                        git pull ${GIT_REPO} main
                        
                        # ใช้คำสั่ง sed แก้เลขเวอร์ชันในไฟล์ deployment.yaml
                        sed -i 's|image: .*|image: ${DOCKER_IMAGE}:${TAG_VERSION}|' deployment.yaml
                        
                        # Push กลับ GitHub
                        git add deployment.yaml
                        git commit -m "Jenkins updated version to ${TAG_VERSION}"
                        git push https://${GIT_USER}:${GIT_PASS}@github.com/KoniPN/devops-lab-project.git HEAD:main
                    """
                }
            }
        }
    }
}