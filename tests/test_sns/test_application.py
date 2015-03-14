from __future__ import unicode_literals

import boto
from boto.exception import BotoServerError
from moto import mock_sns
import sure  # noqa


@mock_sns
def test_create_platform_application():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
        attributes={
            "PlatformCredential": "platform_credential",
            "PlatformPrincipal": "platform_principal",
        },
    )
    application_arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']
    application_arn.should.equal('arn:aws:sns:us-east-1:123456789012:app/APNS/my-application')


@mock_sns
def test_get_platform_application_attributes():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
        attributes={
            "PlatformCredential": "platform_credential",
            "PlatformPrincipal": "platform_principal",
        },
    )
    arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']
    attributes = conn.get_platform_application_attributes(arn)['GetPlatformApplicationAttributesResponse']['GetPlatformApplicationAttributesResult']['Attributes']
    attributes.should.equal({
        "PlatformCredential": "platform_credential",
        "PlatformPrincipal": "platform_principal",
    })


@mock_sns
def test_get_missing_platform_application_attributes():
    conn = boto.connect_sns()
    conn.get_platform_application_attributes.when.called_with("a-fake-arn").should.throw(BotoServerError)


@mock_sns
def test_set_platform_application_attributes():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
        attributes={
            "PlatformCredential": "platform_credential",
            "PlatformPrincipal": "platform_principal",
        },
    )
    arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']
    conn.set_platform_application_attributes(arn,
        {"PlatformPrincipal": "other"}
    )
    attributes = conn.get_platform_application_attributes(arn)['GetPlatformApplicationAttributesResponse']['GetPlatformApplicationAttributesResult']['Attributes']
    attributes.should.equal({
        "PlatformCredential": "platform_credential",
        "PlatformPrincipal": "other",
    })


@mock_sns
def test_list_platform_applications():
    conn = boto.connect_sns()
    conn.create_platform_application(
        name="application1",
        platform="APNS",
    )
    conn.create_platform_application(
        name="application2",
        platform="APNS",
    )

    applications_repsonse = conn.list_platform_applications()
    applications = applications_repsonse['ListPlatformApplicationsResponse']['ListPlatformApplicationsResult']['PlatformApplications']
    applications.should.have.length_of(2)


@mock_sns
def test_delete_platform_application():
    conn = boto.connect_sns()
    conn.create_platform_application(
        name="application1",
        platform="APNS",
    )
    conn.create_platform_application(
        name="application2",
        platform="APNS",
    )

    applications_repsonse = conn.list_platform_applications()
    applications = applications_repsonse['ListPlatformApplicationsResponse']['ListPlatformApplicationsResult']['PlatformApplications']
    applications.should.have.length_of(2)

    application_arn = applications[0]['PlatformApplicationArn']
    conn.delete_platform_application(application_arn)

    applications_repsonse = conn.list_platform_applications()
    applications = applications_repsonse['ListPlatformApplicationsResponse']['ListPlatformApplicationsResult']['PlatformApplications']
    applications.should.have.length_of(1)


@mock_sns
def test_create_platform_endpoint():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
    )
    application_arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']

    endpoint = conn.create_platform_endpoint(
        platform_application_arn=application_arn,
        token="some_unique_id",
        custom_user_data="some user data",
        attributes={
            "Enabled": False,
        },
    )

    endpoint_arn = endpoint['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']
    endpoint_arn.should.contain("arn:aws:sns:us-east-1:123456789012:endpoint/APNS/my-application/")


@mock_sns
def test_get_list_endpoints_by_platform_application():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
    )
    application_arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']

    endpoint = conn.create_platform_endpoint(
        platform_application_arn=application_arn,
        token="some_unique_id",
        custom_user_data="some user data",
        attributes={
            "CustomUserData": "some data",
        },
    )
    endpoint_arn = endpoint['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']

    endpoint_list = conn.list_endpoints_by_platform_application(
        platform_application_arn=application_arn
    )['ListEndpointsByPlatformApplicationResponse']['ListEndpointsByPlatformApplicationResult']['Endpoints']

    endpoint_list.should.have.length_of(1)
    endpoint_list[0]['Attributes']['CustomUserData'].should.equal('some data')
    endpoint_list[0]['EndpointArn'].should.equal(endpoint_arn)


@mock_sns
def test_get_endpoint_attributes():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
    )
    application_arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']

    endpoint = conn.create_platform_endpoint(
        platform_application_arn=application_arn,
        token="some_unique_id",
        custom_user_data="some user data",
        attributes={
            "Enabled": False,
            "CustomUserData": "some data",
        },
    )
    endpoint_arn = endpoint['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']

    attributes = conn.get_endpoint_attributes(endpoint_arn)['GetEndpointAttributesResponse']['GetEndpointAttributesResult']['Attributes']
    attributes.should.equal({
        "Enabled": 'False',
        "CustomUserData": "some data",
    })


@mock_sns
def test_get_missing_endpoint_attributes():
    conn = boto.connect_sns()
    conn.get_endpoint_attributes.when.called_with("a-fake-arn").should.throw(BotoServerError)


@mock_sns
def test_set_endpoint_attributes():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
    )
    application_arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']

    endpoint = conn.create_platform_endpoint(
        platform_application_arn=application_arn,
        token="some_unique_id",
        custom_user_data="some user data",
        attributes={
            "Enabled": False,
            "CustomUserData": "some data",
        },
    )
    endpoint_arn = endpoint['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']

    conn.set_endpoint_attributes(endpoint_arn,
        {"CustomUserData": "other data"}
    )
    attributes = conn.get_endpoint_attributes(endpoint_arn)['GetEndpointAttributesResponse']['GetEndpointAttributesResult']['Attributes']
    attributes.should.equal({
        "Enabled": 'False',
        "CustomUserData": "other data",
    })


@mock_sns
def test_publish_to_platform_endpoint():
    conn = boto.connect_sns()
    platform_application = conn.create_platform_application(
        name="my-application",
        platform="APNS",
    )
    application_arn = platform_application['CreatePlatformApplicationResponse']['CreatePlatformApplicationResult']['PlatformApplicationArn']

    endpoint = conn.create_platform_endpoint(
        platform_application_arn=application_arn,
        token="some_unique_id",
        custom_user_data="some user data",
        attributes={
            "Enabled": False,
        },
    )

    endpoint_arn = endpoint['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']

    conn.publish(message="some message", message_structure="json", target_arn=endpoint_arn)