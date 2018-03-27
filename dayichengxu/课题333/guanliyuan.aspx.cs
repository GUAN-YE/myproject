using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data.SqlClient;
using System.Data;

public partial class guanliyuan : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {

    }
    protected void Button1_Click(object sender, EventArgs e)
    {
        string username = TextBox1.Text.Trim();
        string pwd = TextBox3.Text.Trim();
        SqlConnection conn = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
        conn.Open();
        string strsql = "select * from guanliyuan where name='" + username + "'";
        SqlCommand cmd = new SqlCommand(strsql, conn);
        SqlDataReader dr = cmd.ExecuteReader();
        if (dr.Read())
        {
            string psd=dr.GetString(dr.GetOrdinal("id")).Trim();
           /* Session["name"] = dr["name"];
            Session["id"] = dr["id"];*/
            if (pwd == psd)
            {
                Response.Redirect("~/houtai.aspx");
            }
            else
            {
                Response.Write(@"<script language='javascript'>alert('密码不对');</script>");
            }

        }
        else
        {
            Response.Write(@"<script language='javascript'>alert('没有该用户');</script>");
        }
    }
}
