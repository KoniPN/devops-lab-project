pipeline {
    agent {
        kubernetes {
            // กำหนดหน้าตาของ Pod ที่จะใช้รันงานนี้
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              # 1. Container สำหรับ Build Image (Kaniko)
              - name: kaniko
                image: gcr.io/kaniko-project/executor:debug
                command: ["/busybox/cat"]
                tty: true
                volumeMounts:
                  - name: docker-config
                    mountPath: /kaniko/.docker
              
              # 2. Container สำหรับ Scan Security (Trivy)
              - name: trivy
                image: aquasec/trivy:latest
                command: ["/bin/sh", "-c", "sleep 3600"] # สั่งให้ตื่นรอไว้
                tty: true
                
              # 3. (Default) jnlp container มีอยู่แล้ว ไม่ต้องประกาศเพิ่ม (เอาไว้รัน git/sed)
                
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

    environment {
        // ชื่อ Image ของคุณ
        IMAGE_NAME = "konipn/devops-lab"
        TAG = "v1-${BUILD_NUMBER}"
        
        // Git Repository
        GIT_REPO = "https://github.com/KoniPN/devops-lab-project.git"
        GIT_CREDS_ID = "github-login" // ชื่อ Credential ID ใน Jenkins
    }

    stages {
        // --- 1. สแกน Code (Filesystem) ---
        stage('Scan Code for Secrets') {
            steps {
                container('trivy') {
                    echo "--- 🔍 Scanning Source Code for Secrets ---"
                    // สแกนหา Secret Key ที่เผลอลืมทิ้งไว้
                    // --exit-code 1 : เจอแล้วหยุดเลย
                    sh "trivy fs --exit-code 1 --security-checks secret ."
                }
            }
        }

        // --- 2. Build & Push Image (Kaniko) ---
        stage('Build & Push Image') {
            steps {
                container('kaniko') {
                    echo "--- 🏗 Building Docker Image ---"
                    // Kaniko จะ Build และ Push ไปให้เลยในคำสั่งเดียว
                    // *หมายเหตุสำหรับ Mac M1/M2: Kaniko จะ Build ตาม CPU เครื่อง 
                    // ถ้า Server ปลายทางเป็น Intel (AMD64) ให้เพิ่ม --customPlatform=linux/amd64
                    sh """
                    /kaniko/executor \
                        --context `pwd` \
                        --destination ${IMAGE_NAME}:${TAG} \
                        --customPlatform=linux/amd64
                    """
                }
            }
        }

        // --- 3. สแกน Image (Remote) ---
        stage('Scan Image for Vulnerabilities') {
            steps {
                container('trivy') {
                    echo "--- 🛡 Scanning Remote Image ---"
                    // ดึง Image ที่เพิ่ง Push ขึ้นไปมาสแกน
                    // สแกนหา CRITICAL เท่านั้น และข้ามอันที่ยังไม่มี Patch แก้
                    sh "trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed ${IMAGE_NAME}:${TAG}"
                }
            }
        }

        // --- 4. แก้ Manifest และ Push Git (GitOps) ---
        stage('Update Deployment Manifest') {
            steps {
                // ขั้นตอนนี้รันใน Container ปกติ (jnlp) ซึ่งเป็น Linux -> ใช้ sed ปกติได้เลย!
                withCredentials([usernamePassword(credentialsId: GIT_CREDS_ID, passwordVariable: 'GIT_PASS', usernameVariable: 'GIT_USER')]) {
                    sh """
                        git config user.email "jenkins@example.com"
                        git config user.name "Jenkins Bot"
                        
                        git pull ${GIT_REPO} main
                        
                        # ใช้ sed แบบ Linux ปกติ (ไม่ต้องมี '' เหมือนใน Mac)
                        sed -i 's|image: ${IMAGE_NAME}:.*|image: ${IMAGE_NAME}:${TAG}|' deployment.yaml
                        
                        git add deployment.yaml
                        
                        # อย่าลืม [skip ci] เพื่อกัน Loop
                        git commit -m "Update image to ${TAG} [skip ci]"
                        
                        git push https://${GIT_USER}:${GIT_PASS}@github.com/KoniPN/devops-lab-project.git HEAD:main
                    """
                }
            }
        }
    }
}