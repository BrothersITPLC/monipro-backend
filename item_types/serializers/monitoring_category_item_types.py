from rest_framework import serializers

from item_types.models import MonitoringCategoryAndItemType


class MonitoringCategoryAndItemTypeSerializer(serializers.ModelSerializer):
    template = serializers.SerializerMethodField()

    class Meta:
        model = MonitoringCategoryAndItemType
        fields = [
            "id",
            "name",
            "category_description",
            "category_long_description",
            "template",
        ]

    def get_template(self, obj):
        """
        obj.template is a list of dicts. For each dict (section), return only:
          - name
          - template_description
          - template_id
        (we deliberately skip any “item_types” key so it never appears in output)
        """
        raw_template = obj.template or []
        filtered = []

        for section in raw_template:
            filtered.append(
                {
                    "name": section.get("name"),
                    "template_description": section.get("template_description"),
                    "template_id": section.get("template_id"),
                }
            )

        return filtered

    # def get_templates(self, obj):
    #     """
    #     `obj.template` is stored as a list of dicts. For each dict in that list,
    #     we only want to return:
    #       - name
    #       - template_description
    #       - item_types (but within item_types, only name and local_item_id)
    #     """
    #     raw_template = obj.template or []
    #     filtered = []
    #     for section in raw_template:
    #         section_name = section.get("name")
    #         section_description = section.get("template_description")

    #         raw_item_types = section.get("item_types", [])
    #         filtered_items = []
    #         for it in raw_item_types:
    #             filtered_items.append(
    #                 {
    #                     "name": it.get("name"),
    #                     "local_item_id": it.get("local_item_id"),
    #                 }
    #             )
    #         filtered.append(
    #             {
    #                 "name": section_name,
    #                 "template_description": section_description,
    #                 "item_types": filtered_items,
    #             }
    #         )

    #         return filtered
