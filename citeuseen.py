import re
import tldextract
import requests
from useragent import USERAGENT
from redis_init import REDIS_KEY_PREFIX, rediscl
import json

VERSION = "0.1"

REVIDS_URL = "https://gitlab-content.toolforge.org/kevinpayravi/cite-unseen-revids/-/raw/main/revids.json?mime=text/plain"
API_URL = "https://meta.wikimedia.org/w/api.php"

CACHE_KEY = f"{REDIS_KEY_PREFIX}:cite_unseen_rules"
CACHE_TTL = 86400  # 1 day in seconds

CITE_UNSEEN_CATEGORY_DATA = {
        # Advocacy groups
        "advocacy": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAPCAMAAAA1b9QjAAAAbFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0Iv+qAAAAI3RSTlMA1A5E+vZW38mMJx7s2aOZjWdaQzoUCvHkyrmvhXx2bWBTMqn0tOoAAAB/SURBVBjTZc9XDoQwDARQZzc9lKVub/j+d8SMAIGYH8svsSXTLt1D7WFwzKctfAxD4hmx4camUiKB1zwjTWIYUeGXiERamt8v0kLyg7hl6v7+d5CGSl6ii4TN1H6l87YqM77WEIoihdT+pVlDepEce5tsvsILWVDyDrWW3xBkBEQGDke/jOMVAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # Blog posts
        "blogs": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAARCAMAAAAMs7fIAAAAclBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACa4vOeAAAAJXRSTlMA+/J3Bq43Mxb3x7OnnJl8Xkoc6ubLoVhNPCgj3dzDkI1ycVZUCH5LxQAAAJZJREFUGBkFwYVhAgEAALG84A51t9t/xSaG2/3DeQ0AVQ27ZwCqqnavAD9f+7uqxkcALI9D1QlYXme8LqpOoMb9E6ah+oWqtiv+hhqvqKrNmalaYL2a3qse2VVLME9DbVZehloAnob64FibtXk6XJiqi+fq7KG6mN9qz60OxurIqUYWtXVffbOsrj7rzst2PMysq5Wpxn9NeBK2TnaptgAAAABJRU5ErkJggg==",
            "count": 0,
        },

        # Book publications
        "books": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAMCAMAAACz+6aNAAAAWlBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACLSV5RAAAAHXRSTlMAqt7QCRnpffrWSSry7cehoHVuRD0sJuLamGkfHurrquoAAABVSURBVAjXvYjJEYAgEMBWQO5bxHP7b1OBsQXzSSago5KSHAWq8NzRqIHnC1hN1lthGNwnBwKdgnoE/Q7D+ZdjlrWd5nY2wRGRZEz7aycUhKmjJB0RHg2VBO5eX4k3AAAAAElFTkSuQmCC",
            "count": 0,
        },

        # Community-created news
        "community": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAQCAMAAADH72RtAAAAaVBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnbPKNAAAAInRSTlMAmWPM27eThIB/06+fjV0lD/r1yLuzqaRzTD8dmGpTUBYCKhLQsAAAAH1JREFUGNONi0kOAjEMBGMgCUy22VfW/v8jiU3EaQ5TUkvlkqz2qI3fRDYfapEAjCIDYEUM4NRc6aSBIOU9ufQCUKVhkq94JzIWmYWIHh+1gjnldSNbVOyobOz92jVZr1Jmc2b0sy2lyRN6XUp7K+XiuDD/wsfhstAPq3b5AqlTD1RMmHJ5AAAAAElFTkSuQmCC",
            "count": 0,
        },

        # Community-maintained sources (editable)
        "editable": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAPCAMAAADeWG8gAAAAvVBMVEUAAABMTEw1NTUdHR0+Pj7o6Oj///8/Pz8pKSkuLi5TU1NXV1dcXFxiYmKMjIywsLDExMT///////9tbW0xMTFfX19KSkpFRUVUVFRMTExHR0dZWVlgYGBra2taWlp2dnaEhIRsbGxmZmZ8fHygoKCOjo6Dg4OqqqqXl5ekpKSmpqacnJyhoaG7u7unp6ezs7O7u7vHx8ft7e3///////8AAAAjIyMGBgZUVFRHR0cLCwtlZWVOTk4iIiIVFRWrycPlAAAANXRSTlMA9P7++R8F/v798+rm3rFcOwkC/v38+PHt7e3r6efi397e1My6uberoZOLh4Z9cnFZMSggDCg5MJMAAACOSURBVBgZXcGFEoJQAATAe6SUgt3dXUcZ//9ZMgYM7iJ1HRzxZ0L/jExJ2AuyiIwq0X+wqyFVHpF3Go11GT8r8sagTdonfLgyw4A9JuSlhoRn8lmlKPKtub8AM7JG2dUEP2KUAlbIrXoo8AsmdSmSCjFT2A31kDnAnFHdUBRFiJZl9R1nDHT8DfK8qYq8F7oKGQbJNCvvAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # State-affiliated or government sources
        "government": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAQCAQAAABaOFzUAAAA2ElEQVQoz4XRPUoDURTF8d+MMG8gCpbRBWghlmLjIuwsrdyErY32U/mxA1MJCgpauAEFKzuLIJEQVFCCMo7FTGQSkngut3jnfzivuNS16MCTfQvGatmRvkKh0HdoaRiva8krPJjcqbUSz7oZgfW51ojMaNqxMfbzW8eeY7m2K5zL9NzJPHiRucSFtp8y3VTYwqMMJ+6xrTAPMQh/G5BIa14VSarnAIbKS4dbUiT/t4SRljC5JdS8KkLHt1jPJz684kunpBE27ZmkXWes6k45QNdK5N2caXr7BW+yUjtO1UbwAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # News articles
        "news": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAARCAMAAAAMs7fIAAAAYFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD6T+iNAAAAH3RSTlMAupk7insrItNVS0O/F28fZWFF48uxSDIMCO+0oIAO/8GCqwAAAIBJREFUGNOdy9sSwiAMRdEDFGmQS6Gttd74/78UkXTGV9dDZrInQXK3RTCXAAhkjcPqgTtOA/LYELQCxuk5wJ8b3wpRGKK1dld1mE9B/ZpKKYZCCNtP8THGFxclpfS6jswFBy4X0dG/N1yS/FpW2ctjM50DcBXYHZq2VOTmWTD1Bls+BmmlzBpEAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # Opinion pieces
        "opinions": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAOCAMAAAD+MweGAAAAb1BMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABt6r1GAAAAJHRSTlMA+xH1Iph8OCYY3MWiLe/p1sq8lI53cGxiV0EM6rGwj2pNSjP1ocsVAAAAgUlEQVQIHV3BRQLCMABFwZ+m7q447/5nJC3dwIzizODYetYpA0yfbN5BjgHGV8qXzTcBdWyBISkaIBCQP4DWu84FUCmFIARugxljwOhpCUJ2U5IBRrqzhOyiDsdIfaiJXdfglNJbig1OFODkOiwXoLRA6+mU+E6RsuqXX636E0X6AFnuEKR6+rcNAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # Predatory journals
        "predatory": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAOCAMAAAAVBLyFAAAAmVBMVEUAAAC/AADAAADAAADAAAC/AAC+AAC/AAC/AAC/AAC/AADAAAC/AAC/AAC/AADAAAC/AADAAAC/AAC/AADEAAC/AADXYWHRS0vMOTnGHh7AAADAAAC+AAC/AAC/AADGAAC/AAD////XXFzHHx/++vr77u733NzQRETMNDTJJibDEBD99vb78PD55ubzzs7xyMjuurrSTEzBCQmtvS+6AAAAIHRSTlMApFWZXe5mRPU1085j39zWnol3Jw/49PPy8ObFloBsCQk/Lh0AAACMSURBVBjTVY7nDsIwDAYdoNCkaeliL6fpZvP+D0djBZHer9NZlj6QU+KUXc5HI7EEFs8NqYjCcO/56DNgMyAyDwnvnyDCd4td4aZlU96Ku1q7qX8qpeqdkwQ2Qxo9irZSpbpunBTo+qFf1dZNqHv8dOYxWRh4HqCBpqKduLLCgE+Iw3CXZBwseZr8/AvR2g1q3xyaTQAAAABJRU5ErkJggg==",
            "count": 0,
        },

        # Press releases
        "press": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAOCAMAAAD+MweGAAAAPFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQLyYwAAAAE3RSTlMAzHczU/m4lm8wHL6timZBPQwdu570zwAAAFxJREFUCNetyDkOw0AMBEGS5p663f//q1eioUCxKhhgWi4lAanI7WBx94Xjep9ho46tbOcRnt4sOhEm/Zd1J+zrWVTVm4bmY6SatW6hN7MqGeZCKDNk+eYEt5T7D9g7DD/ysJyVAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # Satirical or parody content
        "satire": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAARCAYAAAAG/yacAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5wceCDI64ByhXQAAAPFJREFUKM+V0zFKQ0EQBuBvn4pWClaWYiF6Ck+Qy+Qi6VLkFNbpxEOYMoQQrCRqY0h8azML6+NJ4g/LMjP/zD/8y8IYLR4x0I9B1FuME3KH8IoXfOAc97iqCQnfcW9j0lmP0hcanCAXpTaSBduI2yAWtGiKUtMzfYfjnnwrlDadQq5OjQ1yUVg7DOt6jYwJbjDqKI0iP4l4l6piOkApI9XvtKucPIohuTIqFWNSceMfSmAVwXxPwzx4qwazSH7uaSr1GQwrM6Z/NEwrzjDhNLqvg/COJ7zhEg+4qFa8K5Nusei8T/csgteLZyzjaywj/oUf7bdVPf0Xy7cAAAAASUVORK5CYII=",
            "count": 0,
        },

        # Social media
        "social": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAARCAYAAAA7bUf6AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAALNSURBVDhPjVNLSFRhFD7/f++MzIyZRrUxrUUR1JhE0QPaBBUIFW0KeiwqcvKZjxY9iEwoCFroOD7CFAJpUSatWriQEqGEICjLIkyamewlhOaM8/De//Td21VmUdgHwzn/Od//3XPOf4Yy0UAN8vCGBjcRCyf0X7DJp9d3LdFcsVa4BxCIMwlDCEowcVyQiFkW1JiAZaZfyE0Sk9eXbd5oGj6f0C0R3R3vhpnx+cx8K2jFFkPA37QzHtM74J4U1WuDOUkP/3CZ+vL20arYHwpROlSw1SSZ7akOP010rF6jDN7iq470OWkbpf7m3qShlcmUm3MFi2SmgAWDaC9ms9/y2TB3SMFH7UQmhJj26KkV0vJZsGYHgVhLfvFsqLBfCFHPRLWzoYI02D3MoiQeKhxKtq065FBxkV0sslxS6VKDii1mwcue97pUV8D4gLGP43cVgx7GUFNC48uzM+4nDhUQmOmcS7oNiGRUImvGUu7Kzy9A+A6hqLcqehMCLyGW9lZEh5ZdHJ92qOiGXFLqujRQCypZEEk2569Lhgpvw92O+Da0Mwr2cZyXJloLehLthXtsIoCnd5FhoB3NQCW00E4W65OQHGDmd9iZMAQGQX+FfZkgRQM4jzlUXBO6EppuXwZZWNtq+3XhqayKSC/m8AiXH3qrIuWK+Ba++txzLnrXUx7+ZPEsYPBZLE1NqmROBIT016K83U7ORtoQ9+bUXJvl/0zRoDLVJTvhoKa4KRdms1tzf7TXPuBvvo4vVxKpdnT2jSV/ufO61l6sM/7gESkoV5FiTQmFf5VCS160exaDfdY5UltmiwCi1B88BXsMgQLYlZ1vavIC/mA9Xu4aduQVisdlMgWTiTbi2K3H+SNT3Y3UqOZFFlC6MbhPCH6gmE5IKfqUUge73tb1O+m/YuFV5sG6OYHWfCj1Po4XFhP4JwKbmneVFrWUOMdFQPQbGOYih834xvIAAAAASUVORK5CYII=",
            "count": 0,
        },

        # Sponsored content
        "sponsored": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAASCAYAAAC9+TVUAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5wceCRIMu+B6UQAAAUVJREFUOMuN079KXFEQx/HPVQwqEgIpU2yRzpSBFG7lK+QNtjeNQjqxCYivkCovkfRWQdhlCx9ALGyWgIWBsFl3b5o5MjneKw4Md5j5zu/8m8v/9gXXWGBc1caRvw6u0y7Rhq9SfNuTvyyNa0nkPL4tmtTwKgk0EWf+kR0HtIymVUfcBvdgTYrXA9rCi2iqbQ1/8Sfxj2yUzvyUj/qOcvRMgeJHtcAw3cU8tjyvmnK+3M0wi0wiuaie8gc+4meVL9wki+RC+X7GS7wJ5rSHe3idktxIc/Ia+3iLA9xhN9UL38A0CvfpXlp8iwU28ClEcr3wU2msVx2jfYUPGOBdD3fbhOJ6NfLwHnvYwTbO8LuDW8JNzza/YjMWGOB7z7Fv4CLNQVsBv2I651U+8xdw2POrL6phu+/hDsucnGDWAayS1wKz6PMP8f7HxLFPnyIAAAAASUVORK5CYII=",
            "count": 0,
        },

        # Tabloids
        "tabloids": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAARCAMAAAAMs7fIAAAAe1BMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC9eBywAAAAKHRSTlMA33YN9+rLup5pZkU+8drRtKqTjF9aUyslHxsF4tXDwqujmYaBXBQIt6ZAsgAAAH1JREFUGBl1wVUWwjAABMBNUndXXPf+J4TIa39gBv9cCykVdmPIrxa7mloFvOE01DygnWFF1Dyl4jushVoNmQVwyuB88ZMkfQo4vS+jg+qG/ghrbkiKeE2zEEaa0zi9xg7alNMJYUXcZDAENw8YiUenmGAtcVX6IrgNK376AFE7D6Mmxn6bAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # TV programs
        "tvPrograms": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAARAgMAAABGA69pAAAADFBMVEUAAACoqKgAAAA1NTWxW1e8AAAAAnRSTlMAWWQkJGgAAAA4SURBVAjXY2BgaGhgAIJGMPnoAIhUYwABayBmWrVqAQMD16pVKxgYNIAMILlqVRd+EqISogtqAgBQEBiFRNOi6QAAAABJRU5ErkJggg==",
            "count": 0,
        },

        # Reliability: Blacklisted
        "blacklisted": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAAWlBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD////u7u7o6OgpKSkMDAy0tLT7+/v5+fl+fn58fHw5OTklJSUhISG1tbWsrKyjo6MkJCR7e3s8PDxKkGAPAAAACnRSTlMAvI4+GrPi4bSxfq7qvQAAAHZJREFUCNddj0sSwjAMQ/MtICexk/QDFO5/TXDpgol2b0a2JKPyLkbnzU/B4pANB03gLtIZk7LFO1WimhbY7x04PdacyzMxvHHotWAvWNsMZ664Uy7AlkkQTfzH22nedhQ1D680aEmNqGnQWWMWeTEuYSw5TPgAC+IHcILUzWIAAAAASUVORK5CYII=",
            "count": 0,
        },

        # Reliability: Deprecated
        "deprecated": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAARCAMAAAAMs7fIAAAAq1BMVEUAAAAUBQUTBQWzJCT///+uIyOwIyOsIiJKEBBLDw9wFhZsFRVHDg67u7tgLS2OIiLLy8ttWVlkPj5kKyv6+vry8vLu7u7j4+Pc3NzX19e3t7eysrKdmJhpVFRhNzdWNDR6IyOhISHp6eno5+fY1tbDw8O6tbWqqamoqKiakJCQkJCQhYWKfX1lSkpYPj5aNTVEMjJnMDBcLy99KiqDKCimISGWICBAHBwsGRlV2YqAAAAAA3RSTlMAp597gGAlAAAAqklEQVQY02XQ1xKCMBAFUHE3BBUSlCLSsffe/v/LTLIjL9ynzJk7s5vt6fTdgY5rqTfBiNs6fGi1ACBFA8AUGWDAg2v4fRqiRvPxc9wXQORygGCTeOiNQYW7PYcBlLOpkccNmGNkQiKPJ7CV2Er8beZlxTkWbSdBxGi5OLz/nVLBPMXwAqpDsyLEFHEn9Syzj8wRVxhX7YoM7mtEv3oR0Na1EDUj6P69e58fVvYMNLFQgRAAAAAASUVORK5CYII=",
            "count": 0,
        },

        # Reliability: Generally reliable
        "generallyReliable": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAAbFBMVEUAAAAsoCwsoSw+qD4toS0roCstoi0uoS4snyw8qDwtoC0toC0soCwuny4toC0toC3///8voi8toS0soCzo9egyozLp9enj8+PD5MORzZGOzI5GrEa/4r/e8N7M6Mxxv3FBqkH0+vTy+fLE5cSRPYNXAAAAEHRSTlMAsxr9vo4/5JD9wbw/PeaP9lvV4AAAAIVJREFUCNclzlsWgyAMBFBQRKu1TXgp+Gy7/z2WgfniHpKTEchzkHLQoqYZrWlbY1VT9OIYiELkHh55pZKVVd6zser8JKvFYEL985cznZAtfU+i3W8LPSR4+V8R+DZhuT1DGNY20nFvjoiSnYVQ+dAB7TyhRs8pyyXUgFUtOUGI7qTsZrz+IPgKG81qz+sAAAAASUVORK5CYII=",
            "count": 0,
        },

        # Reliability: Generally unreliable
        "generallyUnreliable": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAASFBMVEUAAADMAADMAADPAADMAADMAADMAADNAADMAADNAAD////MAAD99fXsnp7pj4/nhobib2/RGBjia2vojY3jcXHYPz/YPDzRGhqXVefLAAAACnRSTlMA8c8VVPOChINSyGF/kwAAAHJJREFUCNc9z9sSwyAIRVGQaFLAVs3t//+0gE3325pxnANYtKac00YQLXgftbaOS0hOZUuHmAlP2TkaSLDe+pZPUHuBdDA/bgly5b8rAhrDk6nxz/F46/rYvyIcHO1yIfmMMWdc8poje4uRJo+Kn1D8hC/MLAbL8liTMwAAAABJRU5ErkJggg==",
            "count": 0,
        },

        # Reliability: Marginally reliable
        "marginallyReliable": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAOCAMAAAAR8Wy4AAAAjVBMVEUAAAD2eQD1eQD2eQD1eQD1eQD1eQD1eAD0eQD0eAD4egDycwD/gAD/cgD1egD1eQD1eQD1eQD1eQD2eQD2eQD0egD0eAD////4nUX1eQD2fgn3kSz3jCTj4N/96tf82LWYmJj7yJb7xI6Li4v5tG9ra2tZWVlISEj2hBT+9+/+9u7GxsbFxcVHR0dGRkYfNpgQAAAAF3RSTlMAu/lq7uDVenUuJBQJBMOvrZaUVFJHRoWjpJIAAAB/SURBVAgdVcEHFoIwEAXAJaEXu3429I71/sczKvJghiZS0oovhE9LW6V2tHDmuuYLzSI7ybLUjuhPcvEcCpY0CcwYrwGxGdDPXuXoe+TqQF+eaIGuA1rh0cdmvAKPO3AbDdKOXAFoGgAVn4hCK4FWltASKySX03iWskuOseK8AfKLCvyhOfkVAAAAAElFTkSuQmCC",
            "count": 0,
        },

        # Reliability: No consensus
        "multi": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAAtFBMVEUAAAAJrd8gteIPsOAAqt0Aq90Aqt0Aqts4veUkt+IWsuAuuuMErN4FrN4ErN4Cq94Cq90Aqt0Aqt8Aqd4Aqt4AqtwApt8Zs+EEq94FrN0Dqt0Dq94AqdwAq90Aqd0Aqd4AqtkAqt8AgP////8Aqt1NxOj1/P74/f7m9/zb8/rE6/e86faq4/Sn4vOc3vKQ2vB70+5Xx+k+v+bs+fzk9vvU8fnO7/iW3PFozetYyOkktuIas+C+oCNVAAAAI3RSTlMA/fv7oJuWI/v7+/rh0MO4tXZGNScSC/vuzb6pjH9xTRsYAtfMWVAAAACbSURBVAjXJctXEsJQCEBRXmKipjd7F9J77Lr/fYnP+8HMGQC480Fz1noA/8Y2TV+9Qs5RajktMMuwXFgn5kq5JDFRnFwNFyCgEjtR16LDikLQFcS2QewHRHUHboxcevs8EScj8CRjemeSW0NySPhE+BBSxSwKHg+KADw15y2/3MUIAGaW2qR5nrTCnsPPGxKmKUhjySJf0/dj4L7guBKsqi+5hQAAAABJRU5ErkJggg==",
            "count": 0,
        },

        # Unknown
        "unknown": {
            "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAJNSURBVDhPVVJNTxNRFJ33prCAdood6EIpi35YKjUsaGzqUjclRsrCXWHjD5CFphJYuBIo3UiiwQTDgoWkC2lNbGJioiEGIhBDFwLFNKGV8GG0KRlMEWbePO+dQmNPcpPzbs65Lzn3EqEOT2hLi/mOrusReHigdEKEbc7JgqLEPsCbowpRM1oscQ+l5DXQgM8nM7/fLnCQZbOHQj5fFoF/FkUaLZcf7VYdAEkac1ut8Z+BwCttdXVP5YCdnbJeKBwx5IuLBdXvf8kkabIoy/HL5zZOwPSlp2eGlUoVXVH+6pFIklmtkxwLOfYODo41n28a+vH3hg2mhFGwvPxDw+kjIx9Ze/szlkrl1HR6W0U+OvrJ+DmT+a6hVpImblBCeJ/LdYmFQg4RB9ntTWR8/JbQ3+81RSJXTb29br62tmdkEQ67aWtrEwRG71LIx9nV1YZ9A0NDQTIwcJ3iD8Xikba0tEtcLpuRJoRHOjtl4NwNRoExpmO/DoODb0l394wJ1kGGh2/W0q9qCcPJufX1Q4gew69HMHiFr6zcFzo6rIbx7EzjGxu/CSi30Phmf/+PmMnkmaE+RywWEhKJ26S5ubH2WzK5hQkTOJAFowERv/N4XjDYnZEeIhpNGXWBzc1fmsMxBeuYmDNMCLP5aRvEnHM6n7P5+W/a6amGy+dYJyeqPjubVdEEq/tqs01J6Pnv5MZkSk3TQO9ZLI3c65W5rnMhlyuRSkXFDOYaGoQHpdLjY9TXjBcwmxPXKOV9QOHI4bwJyXEuphXlYb6qQAjCP3DDM2e6XmppAAAAAElFTkSuQmCC",
            "count": 0,
        }
    }


# Map of source to policy page
CITE_UNSEEN_SOURCE_TO_PAGE = {
    'enAs': 'en:Wikipedia:WikiProject Albums/Sources',
    'enAms': 'en:Wikipedia:WikiProject Anime and manga/Online reliable sources',
    'enJapans': 'en:Wikipedia:WikiProject Japan/Reliable sources',
    'enKoreas': 'en:Wikipedia:WikiProject Korea/Reliable sources',
    'enNppsg': 'en:Wikipedia:New pages patrol source guide',
    'enRsp': 'en:Wikipedia:Reliable sources/Perennial sources',
    'enVgs': 'en:Wikipedia:WikiProject Video games/Sources',
    'zhAcgs': 'zh:维基专题:ACG/來源考量',
    'zhRsp': 'zh:维基百科:可靠来源/常见有争议来源列表',
    'zhVgs': 'zh:维基专题:电子游戏/来源考量'
}

def fetch_revids():
    try:
        r = requests.get(REVIDS_URL, headers={ 'User-Agent': USERAGENT }, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def fetch_wikitext_from_revisions(revids):
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "revids": "|".join(map(str, revids)),
        "rvslots": "*",
        "rvprop": "content",
        "formatversion": "2"
    }
    r = requests.get(API_URL, headers={ 'User-Agent': USERAGENT }, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    texts = []
    for page in data["query"]["pages"]:
        if "revisions" in page:
            texts.append(page["revisions"][0]["slots"]["main"]["content"])
    return "\n\n".join(texts)

def split_sections(fulltext):
    sections = {}
    header_regex = re.compile(r"^==[=]+\s*(.*?)\s*===", re.M)
    matches = list(header_regex.finditer(fulltext))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(fulltext)
        sections[m.group(1).strip()] = fulltext[start:end].strip()
    return sections

def parse_culink_templates(section_text):
    pattern = re.compile(r"{{\s*CULink\s*\|\s*([^}]+?)\s*}}")
    matches = pattern.findall(section_text)
    rules = []
    for m in matches:
        parts = [p.strip() for p in m.split("|") if p.strip()]
        rule = {}
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                rule[k.strip()] = v.strip()
        rules.append(rule)
    return rules

def build_rule_index(fulltext):
    sections = split_sections(fulltext)
    categorized_rules = {}
    for section, text in sections.items():
        rules = parse_culink_templates(text)
        if rules:
            categorized_rules.setdefault(section, []).extend(rules)
    return categorized_rules

def normalize_domain(url):
    ext = tldextract.extract(url)
    return ".".join(part for part in [ext.domain, ext.suffix] if part)

def annotate_url_impl(domain, rules_index):
    annotations = {
        "domain": domain,
        "tags": [],
        "sourcePage": []
    }
    for section, rules in rules_index.items():
        for rule in rules:
            if "url" in rule and domain in rule["url"]:
                annotations["tags"].append(section)
                for prefix, page_link in CITE_UNSEEN_SOURCE_TO_PAGE.items():
                    if section.startswith(prefix):
                        annotations["sourcePage"].append(page_link)
                        break
    return parse_annotations(annotations)

def parse_annotations(data: dict) -> dict:
    tags = data.get("tags", [])
    parsedTags = []
    for tag in tags:
        if tag.startswith("en"):
            tagData = {}
            tagData["language"] = "en"
            tagData['originalTag'] = tag
            for prefix, page_link in CITE_UNSEEN_SOURCE_TO_PAGE.items():
                if tag.startswith(prefix):
                    tag = tag.replace(prefix, "")
                    tagData["sourcePage"] = page_link
                    break
            for key in CITE_UNSEEN_CATEGORY_DATA.keys():
                if tag.lower() == key.lower():
                    tagData["category"] = key
                    tagData["icon"] = CITE_UNSEEN_CATEGORY_DATA[key]["icon"]
                    break
            parsedTags.append(tagData)
        elif tag.startswith("zh"):
            tagData = {}
            tagData["language"] = "zh"
            tagData['originalTag'] = tag
            for prefix, page_link in CITE_UNSEEN_SOURCE_TO_PAGE.items():
                if tag.startswith(prefix):
                    tag = tag.replace(prefix, "")
                    tagData["sourcePage"] = page_link
                    break
            for key in CITE_UNSEEN_CATEGORY_DATA.keys():
                if tag.lower() == key.lower():
                    tagData["category"] = key
                    tagData["icon"] = CITE_UNSEEN_CATEGORY_DATA[key]["icon"]
                    break
            parsedTags.append(tagData)
    data["parsedTags"] = parsedTags
    return data

def build_index_and_cache():
    revids_data = fetch_revids()
    if not revids_data:
        return None
    revids = revids_data.values()
    fulltext = fetch_wikitext_from_revisions(revids)
    rules_index = build_rule_index(fulltext)
    rediscl.setex(CACHE_KEY, CACHE_TTL, json.dumps(rules_index))
    return rules_index

def annotate_url(url) -> dict:
    domain = normalize_domain(url)
    cache_key = f"{REDIS_KEY_PREFIX}:{VERSION}:cite_unseen:{domain}"
    cached = rediscl.get(cache_key)
    if cached:
        data = json.loads(cached)
        data['from_cache'] = True
        data['url'] = url
        return data
    
    rules_index_raw = rediscl.get(CACHE_KEY)
    if rules_index_raw:
        rules_index = json.loads(rules_index_raw)
    else:
        rules_index = build_index_and_cache()
        if rules_index is None:
            return {
                "url": url,
                "domain": normalize_domain(url),
                "tags": [],
                "sourcePage": [],
                "error": "Failed to fetch rules"
            }
    annotations = annotate_url_impl(domain, rules_index)
    rediscl.setex(cache_key, CACHE_TTL, json.dumps(annotations))
    annotations['from_cache'] = False
    annotations['url'] = url
    return annotations

def annotate_url_with_custom_rules(url: str, custom_rules: dict) -> dict:
    return annotate_url_impl(url, custom_rules)
