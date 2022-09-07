from rest_framework.serializers import ModelSerializer
from django_countries.serializers import CountryFieldMixin
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from users.models import User
from datetime import datetime
from workside.models import Event
from business.models import (
    Business,
    Employee,
    BusinessAddress,
    Country,
    City,
    Region,
    EmergencyContact,
    Attendance,
    LeaveRequest
)

from business.services import (
    create_user_for_employee,
    create_employee,
    send_email_to_employee,
    update_user_for_employee,
    update_employee
)


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class RegionSerializer(ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class BusinessAddressSerializer(CountryFieldMixin, ModelSerializer):
    class Meta:
        model = BusinessAddress
        exclude = ['id', 'created_at', 'updated_at', 'business']


class BusinessSerializer(ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'pay_frequency', 'profile_image']


class EmployeePersonalInformationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth']


class EmployeeAddressInformationSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = ['address_line_one', 'address_line_two', 'city']


class EmployeeWorkInformationSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = ['position', 'hourly_rate']


class EmployeeContactSerializer(CountryFieldMixin, ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone']


class EmployeeSerializer(ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    address_information = serializers.SerializerMethodField()
    work_information = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'personal_information', 'contact', 'address_information', 'work_information']

    @staticmethod
    def get_personal_information(obj):
        data = EmployeePersonalInformationSerializer(obj.user, many=False).data
        try:
            data['profile_image'] = obj.profile_image.url
        except Exception:
            data['profile_image'] = None
        return data

    @staticmethod
    def get_contact(obj):
        data = EmployeeContactSerializer(
            obj.user,
            many=False
        ).data
        data['mobile'] = str(obj.mobile)
        return data

    @staticmethod
    def get_address_information(obj):
        return EmployeeAddressInformationSerializer(
            obj, many=False
        ).data

    @staticmethod
    def get_work_information(obj):
        return EmployeeWorkInformationSerializer(
            obj,
            many=False
        ).data

    def create(self, validated_data):
        request = self.context['request']
        employee_user, password = create_user_for_employee(request.data)
        employee = create_employee(employee_user, request.data, request.user)
        send_email_to_employee(employee_user, password)
        return employee

    def update(self, instance, validated_data):
        request = self.context['request']
        employee_user, password = update_user_for_employee(request.data, instance)
        employee = update_employee(employee_user, request.data)
        send_email_to_employee(employee_user, password)
        return employee


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'gender', 'date_of_birth']


class EmergencyContactSerializer(ModelSerializer):
    class Meta:
        model = EmergencyContact
        exclude = ['employee', 'id', 'is_active', 'created_at', 'updated_at']


class BusinessAdminProfileSerializer(ModelSerializer):
    business_information = serializers.SerializerMethodField(read_only=True)
    personal_information = serializers.SerializerMethodField(read_only=True)
    business_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['business_information', 'personal_information', 'business_address']

    @staticmethod
    def get_business_information(obj):
        return BusinessSerializer(
            Business.objects.get(user=obj),
            many=False
        ).data

    @staticmethod
    def get_personal_information(obj):
        return UserSerializer(
            obj,
            many=False
        ).data

    @staticmethod
    def get_business_address(obj):
        return BusinessAddressSerializer(
            BusinessAddress.objects.get(business__user=obj),
            many=False
        ).data


class BusinessEmployeeProfileSerializer(ModelSerializer):
    personal_information = serializers.SerializerMethodField(read_only=True)
    emergency_contact = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['personal_information', 'emergency_contact']

    @staticmethod
    def get_personal_information(obj):
        return UserSerializer(
            obj,
            many=False
        ).data

    @staticmethod
    def get_emergency_contact(obj):
        return EmergencyContactSerializer(
            EmergencyContact.objects.get(employee__user=obj),
            many=False
        ).data


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def update(self, instance, validated_data):
        request = self.context['request']
        User.objects.filter(id=self.request.user.id).update(**request.data['personal_information'])
        if request.user.role == 'Organization Admin':
            Business.objects.filter(user=self.request.user).update(**request.data['business_information'])
            BusinessAddress.objects.filter(user=self.request.user).update(**request.data('business_address'))
        else:
            EmergencyContact.objects.filter(employee__user=request.user).update(**request.data['emergency_contact'])
        return request.user


class LeaveRequestSerializer(ModelSerializer):
    class Meta:
        model = LeaveRequest
        exclude = ('created_at', 'updated_at')

    def to_representation(self, data):
        data = super(LeaveRequestSerializer, self).to_representation(data)
        request = self.context['request']
        if request.user.role == "Organization Admin":
            data['Employee_name'] = Employee.objects.get(id=data['employee']).user.get_full_name()
            del data['employee']
        return data

    def create(self, validated_data):
        request = self.context['request']
        validated_data['employee'] = Employee.objects.get(user=request.user)
        leave_request = LeaveRequest.objects.create(
            **validated_data
        )
        return leave_request


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        exclude = ('created_at', 'updated_at')

    def validate(self, data):
        request = self.context['request']
        if data['status'].__contains__('CLOCK_IN'):
            event = Event.objects.filter(
                start_time__gte=datetime.now(),
                end_time__gte=datetime.now(),
                employees__in=[Employee.objects.get(user=request.user).id]
            )
            print(event)
            if not event.exists():
                raise serializers.ValidationError(_("Event Time not started"))
        return data

    def create(self, validated_data):
        request = self.context['request']
        validated_data['employee'] = Employee.objects.get(user=request.user)
        validated_data['clock_in_time'] = datetime.now()
        attendance = Attendance.objects.create(
            **validated_data
        )
        return attendance


class EarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'profile_image', 'position', 'hourly_rate')

    def to_representation(self, data):
        data = super(EarningSerializer, self).to_representation(data)
        employee = Employee.objects.get(id=data['id'])
        data['name'] = employee.user.get_full_name()
        try:
            data['total_hours'] = Attendance.objects.filter(employee=employee.id).last().total_hours
        except:
            data['total_hours'] = 0
        data['earning'] = employee.get_total_pay_amount()
        return data
