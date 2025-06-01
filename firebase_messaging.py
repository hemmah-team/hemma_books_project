import firebase_admin
from firebase_admin import credentials, messaging

from account.models import Notification, User
from products.models import Product

token = {
    "type": "service_account",
    "project_id": "hemmah-products",
    "private_key_id": "9dfef409cf5eb9d972cb212728003f412541e4d8",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCzECa2lo8oylfr\n4hfSfHKiPV21nSoiSxhTDeZfMO00T8zPR6pJ5dXkrxED4uCPCd90fx1qu4wsIkRN\ntGCIvtJZX8qrbOjXNfd9ioZlcfIgXoqLkCq7LJGRRGGO4D7bXhQBsewjpYrt/vPh\nL5c0xCKF44Fjz4uvOmKwLSSp8Mhbr/5iyySG/Sgt6zCVUQLGCasWidnjv3iBsN96\nQDGMyUcCqzG5Rr+kUZnyylX7OTFH5PX0gpKSWW7vNlMIBMjpb+fNb6btu4NDFSZs\ni/xyPB5xsLHCPSbqbce7vHcqT9kqLGhRu/3dCWs235kIANM3a+kDGt+4hmjhgd+9\n8EiEe8kHAgMBAAECgf9Z4UGNZQV29BotzM8oWE8yIJtpDfqYPBl5lwCLx4NJPsUP\nRmmzriovH7Dqwnb1VX9UennJmVpCzPB8EI5kFWSAeBTC92fonq4b1eyf/xIKLWpd\no3/PdA+dWzWdAfKLKi3gq+5b9jxGOjMwVTMQyWKK0iegcg0rZ6Mhy4cbxkDLxDMU\n21a0T98//IO3/Y100u0awZb6jv9pqvI/okGQ6iWAihr6A0WoILB6ov2fm6VNNA8j\n6GZ6eoJifzvfteqcHDFdMAN7rVrx3aCauF4aq59aD1QxhPdJPcHHF9j1uaq3lgtD\n0HkVmp2QEpzQCo9RBX5tVy2FVcFe6FY6yt/2Ps0CgYEA7/+JJbBeKXRsnuzQ3nA6\nIjtiQ/3zpGjBZJCjDJGAsdtlMk2t6VkKz52q2WyqJM7MlvZqBkHvJTDTWgQ80AKe\nsl1/xWC44lvnd6VcEt4AFnwqN1ezDvKYPm2h7uUXYZp4SWVtobLgjCLII1sOLn8t\nYLhfYN9gII83kp9KUQmKO40CgYEAvwCH4dRUInYKflLTRk8VfwmbvkUgi3BDbyA9\ngje0vCrjKzeQX2taBeLqwMUl68gWqAUibalPauM65FqNnp0NXlRIx0/eGDFyRUAF\nIrUHyCn0r7OOwbGxlzZ+486J5T+Cyoz2On+r9agjEE0D1ND8K8GZazPFHBUz+SxW\nEd5Qp+MCgYAgIH/2eJ6SRBCKUb9AF5vgmzxzR5qG5rMEyEvbUdr9dBYe3sEqHI5S\n7pNBWceI99nxV3kn70mZG+kfArQ1UDR4QgXpoSH+wzjADnW93NP8LpDkKaxBkv4I\nVVq5BRfVK/1wLdC4NZ7Tg5BxEy5Z0RJ9ARFbgWt30FQrH4GuSW2kvQKBgQCXNudd\nHcnCQqvKGO6VUlUVb1jzCS1b13Q7zU2FA28+LcIN2/6b3JS35k+ucCa2hYGSYgZA\nxXNPjzh3w00tju8fiCDaUtvlUXhDZQzrzmCr0rOaStCxfmm36ngJCOJZMa/thi4G\nYD+WzBd+d0qaOR370lkQ6zqZIhw0oCpAGT7HuwKBgQCkTFiecRW71Y6/NEnHRWJe\nv3sM+DozUFY5iN/574v7lEib3mB+cpq3qKILbSywtcFfSxmNAQu7CHRNOSJs93Vf\nrVwfFWYsSDZHCZ8jsT89cXKgkb2fo/d43u23IcDL2cpkbTxP715KNlwKfNQiN6p+\nYwFohaR86In/3eqGYZPYnA==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@hemmah-products.iam.gserviceaccount.com",
    "client_id": "104421185453615186186",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40hemmah-products.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}


cred = credentials.Certificate(token)
if not firebase_admin._apps:
    firebase_admin.initialize_app(
        cred,
    )


def sendMessage(
    seller_user: User,
    buyer_user: User,
    product: Product,
    isApprove: bool = False,
):
    if isApprove:
        m = f"لقد تم مراجعة والموافقة على منتجك ({product.name}). يمكنك الآن رؤيته متاحًا للجميع في متجرنا!"

    else:
        m = f"تم طلب منتجك ({product.name})"
        m = f"قام ({product.buyer.name}) بـ (شراء/استعارة/الحصول على) منتجك ({product.name}). يرجى التواصل معه لتنسيق التسليم."
    for fcm in buyer_user.fcms.all():
        if fcm:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="خبر رائع!",
                    body=m,
                ),
                token=fcm.token,
            )
            messaging.send(message)
        Notification.objects.create(title="طلب", message=m, user=seller_user)


def sendPublicMessage(message: str, title: str):
    messag = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=message,
        ),
        topic="public",
    )

    messaging.send(messag)
    Notification.objects.create(title="طلب", message=message)
