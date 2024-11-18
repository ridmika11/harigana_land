from django.shortcuts import render
from .models import PropertyDetails,ProvinceDetails,DistrictDetails,CityDetails
from django.db.models import Q
from django.http import JsonResponse
import re

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def valuation(request):
    return render(request, 'vehicle_valuation.html')

def result(request):
    return render(request, 'result')


def property_view(request):
    # Get all districts
    districts = DistrictDetails.objects.all()
    #cities = []  # Initialize empty city list
    cities = CityDetails.objects.all()

    max_value = 0
    min_value = 0
    avg_value = 0
    avg_rent_value = 0
     

    # Default form data
    form_data = {
        'district': '',
        'city': '',
        'property_type': '',
        'bedrooms': '',
        'bedrooms_check': False,
        'bathrooms': '',
        'bathrooms_check': False,
        'floor_area': '',
        'floor_area_check': False,
        'land_area': '',
        'land_area_check': False,
        'comfort_features': [],
    }

    if request.method == 'POST':
        # Extract form data
        district_data = request.POST.get('district', '').strip()
        # Split the value to get both parts
        if district_data:
            district_id, district_name = district_data.split(',')
        else:
            district_id, district_name = None, None

        city_data= request.POST.get('city', '').strip()
        if city_data:
            city_id,city_name=city_data.split(',')
        else:
            city_id,city_name = None, None 


        property_type = request.POST.get('property_type', '').strip()
        bedrooms = request.POST.get('bedrooms', '')
        bedrooms_check = request.POST.get('bedrooms_check') == 'on'
        bathrooms = request.POST.get('bathrooms', '')
        bathrooms_check = request.POST.get('bathrooms_check') == 'on'
        floor_area = request.POST.get('floor_area', '')
        floor_area_check = request.POST.get('floor_area_check') == 'on'
        land_area = request.POST.get('land_area', '')
        land_area_check = request.POST.get('land_area_check') == 'on'
        comfort_features = request.POST.getlist('feature', [])

        # Update form_data with submitted values
        form_data.update({
            'district': district_name,
            'city': city_name,
            'property_type': property_type,
            'bedrooms': bedrooms,
            'bedrooms_check': bedrooms_check,
            'bathrooms': bathrooms,
            'bathrooms_check': bathrooms_check,
            'floor_area': floor_area,
            'floor_area_check': floor_area_check,
            'land_area': land_area,
            'land_area_check': land_area_check,
            'comfort_features': comfort_features,
        })

        # Get cities for the selected district
        if district_id:
            district_id = int(district_id)
            #print('district_id:', district_id)
            cities = CityDetails.objects.filter(city_district_id=district_id)
            #print('print2', list(cities))
            
        # Filter properties based on the form data
        filtered_properties = PropertyDetails.objects.filter(
            Q(location__icontains=district_name) & Q(location__icontains=city_name),
            property_type__icontains=property_type
        )

        """if city_name:
            filtered_properties = filtered_properties.filter(location=city_name)"""

        if bedrooms_check and bedrooms.isdigit():
            filtered_properties = filtered_properties.filter(bedrooms=int(bedrooms))

        if bathrooms_check and bathrooms.isdigit():
            filtered_properties = filtered_properties.filter(bathrooms=int(bathrooms))

        if floor_area_check and floor_area.isdigit():
            filtered_properties = filtered_properties.filter(floor_area__gte=int(floor_area))

        if land_area_check and land_area.isdigit():
            filtered_properties = filtered_properties.filter(land_area__gte=int(land_area))

        if comfort_features:
            feature_queries = Q()
            for feature in comfort_features:
                feature_queries &= Q(property_details__icontains=feature) | Q(property_features__icontains=feature)
            filtered_properties = filtered_properties.filter(feature_queries)

        if filtered_properties:
            rented_propeties = filtered_properties.filter(title__icontains='Rent')
            if rented_propeties:  # Check if rented_properties is not empty
                avg_rent_value = sum(
                    float(''.join(re.findall(r'\d+', str(property.price))))  # Ensure property.price is a string
                    for property in rented_propeties
                    if property.price is not None  # Check if property.price is not None
                ) / len(rented_propeties)
            else:
                avg_rent_value = 0  # Default value if no rented properties found       

        if filtered_properties:
            max_value = max(
                                float(''.join(re.findall(r'\d+', str(property.price))))  # Ensure property.price is a string
                                for property in filtered_properties
                                if property.price is not None  # Check if property.price is not None
                            )
            min_value = min(
                                float(''.join(re.findall(r'\d+', str(property.price))))  # Ensure property.price is a string
                                for property in filtered_properties
                                if property.price is not None  # Check if property.price is not None
                            )
            if filtered_properties:
                avg_value = sum(
                                
                                float(''.join(re.findall(r'\d+', str(property.price))))  # Ensure property.price is a string
                                for property in filtered_properties
                                if property.price is not None  # Check if property.price is not None

                            ) / len(filtered_properties)
            else:
                avg_value = 0  # or handle the case differently

        
        
        max_value = f"RS{max_value: ,.2f}"
        min_value = f"RS{min_value: ,.2f}"
        avg_value = f"RS{avg_value: ,.2f}"
        avg_rent_value = f"Rs{avg_rent_value: ,.2f}"
       

        prices = {
            'max_value':max_value,
            'min_value':min_value,
            'avg_value':avg_value,
            'avg_rent_value':avg_rent_value,

        }

        context = {
            'records': filtered_properties,
            'form_data': form_data,
            'districts': districts,
            'cities': cities,
            'prices':prices
            

        }
        return render(request, 'property_valuation.html', context)

    else:
        # Handle GET request - fetch all properties
        all_ad_details = PropertyDetails.objects.all()

        # Populate cities if a district is pre-selected
        if form_data['district']:
            cities = CityDetails.objects.filter(district_id=form_data['district'])
        
        max_value = 0
        min_value = 0
        avg_value = 0

        prices = {
            'max_value':max_value,
            'min_value':min_value,
            'avg_value':avg_value,
            'avg_rent_value':avg_rent_value,


        }

        context = {
            'records': all_ad_details,
            'form_data': form_data,
            'districts': districts,
            'cities': cities,
            'prices':prices,
        }
        return render(request, 'property_valuation.html', context)

def get_cities(request, district_id):
    district_id = int(district_id)  # Get district_id directly from the function argument
    print(district_id)
    if district_id:
        cities = CityDetails.objects.filter(city_district_id=district_id).values('id', 'name_en')
        cities_list = [{'id': city['id'], 'name': city['name_en']} for city in cities]
        return JsonResponse({'cities': cities_list})
    else:
        return JsonResponse({'cities': []})
    
def result(request):
    # Assuming you process form and get district and city
    selected_district = request.POST.get('district')
    selected_city = request.POST.get('city')
    
    # Pass these values to the template
    return render(request, 'result.html', {
        'selected_district': selected_district,
        'selected_city': selected_city,
        # Other context data
    })





